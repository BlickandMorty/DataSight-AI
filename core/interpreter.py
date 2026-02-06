from google import genai
import config

def get_ai_audit(metadata, api_key, return_trail=False):
    """
    rule pass first, then ask gemini for a summary.
    if return_trail is true, return (audit_trail, summary).
    """
    client = genai.Client(api_key=api_key)
    audit_trail = []
    summary = ""
    errors = []
    # simple rule pass: missing values
    nulls = metadata.get('null_counts', {})
    for col, count in nulls.items():
        if count > 0:
            audit_trail.append({
                'description': f"Column '{col}' has {count} missing values.",
                'suggested_fix': f"Fill or drop missing values in '{col}'",
                'fix_function': lambda df, c=col: df.fillna({c: df[c].mode()[0] if not df[c].mode().empty else 0})
            })
    # then ask gemini for a summary
    for model_name in config.get_model_candidates():
        try:
            response = client.models.generate_content(model=model_name, contents=config.AUDIT_PROMPT.format(metadata=metadata))
            summary = response.text
            break
        except Exception as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                errors.append(f"{model_name}: quota exhausted (try later or check billing)")
            elif "NOT_FOUND" in msg or "404" in msg:
                errors.append(f"{model_name}: model not available for this api")
            else:
                errors.append(f"{model_name}: {type(e).__name__}: {e}")
            continue
    if not summary:
        if audit_trail:
            issues = "; ".join(item["description"] for item in audit_trail)
            summary = f"ai summary unavailable. rule-based findings: {issues}"
        else:
            summary = "ai summary unavailable. rule-based findings: no missing values found."
        if errors:
            summary += "\nreasons:\n" + "\n".join(f"- {err}" for err in errors)
    if return_trail:
        return audit_trail, summary
    # older callers expect just the summary
    return summary
