"""
HTMX POST handlers for all 10 AI tools.
Each handler: reads POST data → builds prompt → calls Groq → returns HTML partial.
"""
import html as html_lib
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .groq_client import groq_chat


def _escape(text: str) -> str:
    return html_lib.escape(text)


def _result_html(content: str, copy_id: str = "ai-result") -> str:
    escaped = _escape(content)
    safe = escaped.replace("\n", "<br>")
    return f"""
<div style="animation:fadeIn .3s ease;">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.75rem;">
    <span style="font-size:.875rem;font-weight:600;color:#16a34a;">✓ Generated</span>
    <button onclick="copyResult('{copy_id}')"
      style="font-size:.75rem;padding:.25rem .75rem;border:1px solid #d1fae5;background:#f0fdf4;color:#16a34a;border-radius:.375rem;cursor:pointer;font-weight:500;">
      Copy
    </button>
  </div>
  <div id="{copy_id}" style="white-space:pre-wrap;font-size:.9375rem;line-height:1.75;color:#0f172a;background:#f8fafc;border:1px solid #e2e8f0;border-radius:.5rem;padding:1.25rem;">
{escaped}
  </div>
</div>
"""


def _error_html(msg: str = "Generation failed. Please try again.") -> str:
    return f"""
<div style="padding:1rem;background:#fef2f2;border:1px solid #fecaca;border-radius:.5rem;color:#dc2626;font-size:.875rem;">
  {_escape(msg)}
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# 1. AI Grammar Checker
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_grammar_checker(request):
    text = request.POST.get("text", "").strip()
    if not text:
        return HttpResponse(_error_html("Please paste some text to check."))
    if len(text) > 8000:
        return HttpResponse(_error_html("Text is too long. Please keep it under 8,000 characters."))

    system = (
        "You are a professional editor and grammar expert. "
        "Correct all grammar, spelling, punctuation, and style errors in the user's text. "
        "Preserve their voice and meaning. "
        "First output the corrected text in full, then output a section '--- Changes Made ---' "
        "followed by a concise bullet-point list of the key corrections. "
        "If the text is already correct, say so and explain why it's good."
    )
    user = f"Check and correct this text:\n\n{text}"
    try:
        result = groq_chat(system, user, max_tokens=2000)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "grammar-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 2. AI Summarizer
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_summarizer(request):
    text = request.POST.get("text", "").strip()
    format_ = request.POST.get("format", "bullet")
    length = request.POST.get("length", "medium")

    if not text:
        return HttpResponse(_error_html("Please paste an article or text to summarize."))
    if len(text) > 12000:
        return HttpResponse(_error_html("Text is too long. Please keep it under 12,000 characters."))

    length_map = {"short": "2–3 sentences", "medium": "5–7 points", "detailed": "10–12 points"}
    length_desc = length_map.get(length, "5–7 points")

    if format_ == "paragraph":
        format_desc = f"a concise paragraph summary ({length_desc})"
    elif format_ == "tldr":
        format_desc = "a single TLDR sentence, then 3 key takeaways"
    else:
        format_desc = f"a bullet-point list ({length_desc})"

    system = (
        "You are an expert summarizer. Extract the most important information from text. "
        "Be accurate, concise, and clear. Never add information not in the original."
    )
    user = f"Summarize the following text as {format_desc}:\n\n{text}"
    try:
        result = groq_chat(system, user, max_tokens=1000)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "summary-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 3. AI Email Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_email_generator(request):
    email_type = request.POST.get("email_type", "professional")
    context = request.POST.get("context", "").strip()
    tone = request.POST.get("tone", "professional")
    recipient = request.POST.get("recipient", "").strip()

    if not context:
        return HttpResponse(_error_html("Please describe the purpose of the email."))

    recipient_line = f"The recipient's name is {recipient}." if recipient else ""
    system = (
        "You are an expert business writer. Write clear, effective, professional emails. "
        "Always include: Subject: line, greeting, body, and sign-off. "
        "Keep it concise and action-oriented."
    )
    user = (
        f"Write a {tone} {email_type} email. "
        f"{recipient_line} "
        f"Context / purpose: {context}"
    )
    try:
        result = groq_chat(system, user, max_tokens=800)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "email-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 4. AI Code Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_code_generator(request):
    description = request.POST.get("description", "").strip()
    language = request.POST.get("language", "python")
    include_comments = request.POST.get("include_comments", "yes")

    if not description:
        return HttpResponse(_error_html("Please describe what you want the code to do."))

    comment_instruction = (
        "Include clear inline comments explaining the logic."
        if include_comments == "yes"
        else "Do not add comments; write self-documenting code."
    )
    system = (
        "You are a senior software engineer. Write clean, production-quality code. "
        "Output the code in a fenced code block, then a brief explanation of how it works. "
        + comment_instruction
    )
    user = f"Write {language} code that: {description}"
    try:
        result = groq_chat(system, user, max_tokens=1800)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "code-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 5. AI Meta Description Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_meta_description_generator(request):
    page_title = request.POST.get("page_title", "").strip()
    keywords = request.POST.get("keywords", "").strip()
    page_summary = request.POST.get("page_summary", "").strip()

    if not page_title:
        return HttpResponse(_error_html("Please enter a page title."))

    system = (
        "You are an SEO expert. Write compelling meta descriptions that improve click-through rates. "
        "Each must be under 160 characters, include the target keyword naturally, "
        "have a clear value proposition, and end with a soft call to action. "
        "Output exactly 3 numbered options."
    )
    user = (
        f"Page title: {page_title}\n"
        f"Target keywords: {keywords or 'not specified'}\n"
        f"Page content summary: {page_summary or 'not provided'}\n\n"
        "Write 3 meta description options."
    )
    try:
        result = groq_chat(system, user, max_tokens=600, temperature=0.8)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "meta-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Paraphrasing Tool
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def paraphrasing_tool(request):
    text = request.POST.get("text", "").strip()
    style = request.POST.get("style", "standard")

    if not text:
        return HttpResponse(_error_html("Please enter some text to paraphrase."))
    if len(text) > 5000:
        return HttpResponse(_error_html("Text is too long. Please keep it under 5,000 characters."))

    style_map = {
        "standard": "Rewrite in clear, natural language. Preserve meaning exactly.",
        "formal": "Rewrite in formal, professional academic language.",
        "simple": "Rewrite in very simple language a 12-year-old could understand.",
        "creative": "Rewrite in a more engaging, vivid, and creative way.",
        "fluent": "Rewrite to sound more fluent and native English.",
    }
    instruction = style_map.get(style, style_map["standard"])

    system = (
        "You are an expert writing assistant. Paraphrase text while preserving the original meaning. "
        "Never add new information. Output only the paraphrased text."
    )
    user = f"{instruction}\n\nOriginal text:\n{text}"
    try:
        result = groq_chat(system, user, max_tokens=1500, temperature=0.6)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "paraphrase-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 7. Cover Letter Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def cover_letter_generator(request):
    job_title = request.POST.get("job_title", "").strip()
    company = request.POST.get("company", "").strip()
    skills = request.POST.get("skills", "").strip()
    why = request.POST.get("why", "").strip()
    applicant_name = request.POST.get("applicant_name", "").strip()

    if not job_title or not company:
        return HttpResponse(_error_html("Please enter the job title and company name."))

    name_line = f"The applicant's name is {applicant_name}." if applicant_name else ""
    system = (
        "You are a professional career coach and cover letter specialist. "
        "Write compelling, tailored cover letters that hiring managers actually read. "
        "Structure: opening hook, relevant achievements, why this company, call to action. "
        "Keep it to 3 paragraphs, confident but not arrogant."
    )
    user = (
        f"Job title: {job_title}\n"
        f"Company: {company}\n"
        f"Key skills and experience: {skills or 'not specified'}\n"
        f"Why this company / role: {why or 'not specified'}\n"
        f"{name_line}\n\n"
        "Write a professional cover letter."
    )
    try:
        result = groq_chat(system, user, max_tokens=900)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "cover-letter-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 8. Hashtag Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def hashtag_generator(request):
    topic = request.POST.get("topic", "").strip()
    platform = request.POST.get("platform", "instagram")
    niche = request.POST.get("niche", "").strip()

    if not topic:
        return HttpResponse(_error_html("Please enter a topic or caption."))

    system = (
        "You are a social media growth expert. Generate relevant, high-performing hashtags. "
        "Organize them into: Popular (1M+ posts), Mid-range (100K–1M posts), Niche (<100K posts). "
        "Output 30 hashtags total across all groups. Each hashtag must start with #. "
        "Add a brief tip for best posting time at the end."
    )
    user = (
        f"Platform: {platform}\n"
        f"Topic / caption: {topic}\n"
        f"Niche / industry: {niche or 'general'}\n\n"
        "Generate 30 optimized hashtags in 3 groups."
    )
    try:
        result = groq_chat(system, user, max_tokens=700, temperature=0.8)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "hashtag-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 9. Product Description Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def product_description_generator(request):
    product_name = request.POST.get("product_name", "").strip()
    features = request.POST.get("features", "").strip()
    audience = request.POST.get("audience", "").strip()
    tone = request.POST.get("tone", "professional")

    if not product_name:
        return HttpResponse(_error_html("Please enter a product name."))

    system = (
        "You are an expert eCommerce copywriter. Write product descriptions that sell. "
        "Output:\n"
        "1. Short description (2–3 sentences for product listings)\n"
        "2. Long description (full paragraph with benefits)\n"
        "3. Bullet points (5 key features/benefits)\n"
        "Focus on benefits over features. Use sensory and emotional language."
    )
    user = (
        f"Product name: {product_name}\n"
        f"Key features: {features or 'not specified'}\n"
        f"Target audience: {audience or 'general consumers'}\n"
        f"Tone: {tone}\n\n"
        "Write a complete product description package."
    )
    try:
        result = groq_chat(system, user, max_tokens=1000)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "product-desc-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 10. ATS Resume Checker
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ats_resume_checker(request):
    resume = request.POST.get("resume", "").strip()
    job_description = request.POST.get("job_description", "").strip()

    if not resume:
        return HttpResponse(_error_html("Please paste your resume text."))
    if len(resume) > 10000:
        return HttpResponse(_error_html("Resume text is too long. Please keep it under 10,000 characters."))

    jd_section = f"\nJob description to match against:\n{job_description}" if job_description else ""

    system = (
        "You are an ATS (Applicant Tracking System) expert and senior recruiter. "
        "Analyze resumes for ATS compatibility and give actionable feedback. "
        "Output exactly in this format:\n"
        "ATS SCORE: [X/100]\n\n"
        "KEYWORD GAPS: [list missing keywords]\n\n"
        "FORMAT ISSUES: [list formatting problems]\n\n"
        "TOP IMPROVEMENTS: [5 specific, actionable improvements]\n\n"
        "STRONG POINTS: [what's working well]"
    )
    user = f"Analyze this resume for ATS compatibility:\n\n{resume}{jd_section}"
    try:
        result = groq_chat(system, user, max_tokens=1200, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "ats-result"))


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher map (tool_slug → handler)
# ─────────────────────────────────────────────────────────────────────────────
AI_HANDLERS = {
    "ai-grammar-checker": ai_grammar_checker,
    "ai-summarizer": ai_summarizer,
    "ai-email-generator": ai_email_generator,
    "ai-code-generator": ai_code_generator,
    "ai-meta-description-generator": ai_meta_description_generator,
    "paraphrasing-tool": paraphrasing_tool,
    "cover-letter-generator": cover_letter_generator,
    "hashtag-generator": hashtag_generator,
    "product-description-generator": product_description_generator,
    "ats-resume-checker": ats_resume_checker,
}
