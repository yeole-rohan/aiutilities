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
    <button onclick="copyResult('{copy_id}', this)"
      style="font-size:.75rem;padding:.25rem .75rem;border:1px solid #d1fae5;background:#f0fdf4;color:#16a34a;border-radius:.375rem;cursor:pointer;font-weight:500;">
      Copy
    </button>
  </div>
  <div id="{copy_id}" style="white-space:pre-wrap;font-size:.9375rem;line-height:1.75;color:#0f172a;background:#f8fafc;border:1px solid #e2e8f0;border-radius:.5rem;padding:1.25rem;">
{escaped}
  </div>
</div>
"""


def _markdown_result_html(content: str, copy_id: str = "ai-result") -> str:
    """Like _result_html but renders markdown via marked.js on the client side."""
    escaped = _escape(content)
    return f"""
<div style="animation:fadeIn .3s ease;">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.75rem;">
    <span style="font-size:.875rem;font-weight:600;color:#16a34a;">✓ Generated</span>
    <button onclick="copyResult('{copy_id}', this)"
      style="font-size:.75rem;padding:.25rem .75rem;border:1px solid #d1fae5;background:#f0fdf4;color:#16a34a;border-radius:.375rem;cursor:pointer;font-weight:500;">
      Copy
    </button>
  </div>
  <div id="{copy_id}-raw" style="display:none;">{escaped}</div>
  <div id="{copy_id}" class="ai-markdown-output" style="font-size:.9375rem;line-height:1.75;color:#0f172a;background:#f8fafc;border:1px solid #e2e8f0;border-radius:.5rem;padding:1.25rem;"></div>
  <script>
    (function(){{
      var raw = document.getElementById('{copy_id}-raw').textContent;
      document.getElementById('{copy_id}').innerHTML = marked.parse(raw);
    }})();
  </script>
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
# 11. AI Content Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_content_generator(request):
    topic = request.POST.get("topic", "").strip()
    content_type = request.POST.get("content_type", "blog post")
    audience = request.POST.get("audience", "").strip()
    tone = request.POST.get("tone", "informative")
    keyword = request.POST.get("keyword", "").strip()
    word_count = request.POST.get("word_count", "600")

    if not topic:
        return HttpResponse(_error_html("Please enter a topic."))

    keyword_line = f"Primary SEO keyword to include naturally: {keyword}." if keyword else ""
    audience_line = f"Target audience: {audience}." if audience else ""
    system = (
        "You are an expert content writer and SEO specialist. "
        "Write engaging, well-structured content that ranks and converts. "
        "Use clear H2 subheadings (##), short paragraphs, and a conversational yet authoritative tone. "
        "Include an introduction, 3–4 main sections, and a conclusion."
    )
    user = (
        f"Write a {tone} {content_type} about: {topic}. "
        f"{audience_line} {keyword_line} "
        f"Aim for approximately {word_count} words."
    )
    try:
        result = groq_chat(system, user, max_tokens=2000)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_markdown_result_html(result, "content-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 12. AI Essay Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_essay_generator(request):
    topic = request.POST.get("topic", "").strip()
    essay_type = request.POST.get("essay_type", "argumentative")
    level = request.POST.get("level", "university")
    word_count = request.POST.get("word_count", "500")
    key_points = request.POST.get("key_points", "").strip()

    if not topic:
        return HttpResponse(_error_html("Please enter an essay topic."))

    points_line = f"Key arguments/points to include: {key_points}." if key_points else ""
    system = (
        "You are an expert academic writer. Write well-structured, original essays. "
        "Format: clear introduction with thesis, body paragraphs each with a topic sentence and supporting evidence, "
        "and a conclusion that restates the thesis and synthesises findings. "
        "Use formal academic language appropriate for the level."
    )
    user = (
        f"Write a {level}-level {essay_type} essay on: {topic}. "
        f"{points_line} "
        f"Target length: approximately {word_count} words."
    )
    try:
        result = groq_chat(system, user, max_tokens=2000)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_markdown_result_html(result, "essay-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 13. Instagram Bio Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def instagram_bio_generator(request):
    name = request.POST.get("name", "").strip()
    niche = request.POST.get("niche", "").strip()
    values = request.POST.get("values", "").strip()
    cta = request.POST.get("cta", "").strip()
    vibe = request.POST.get("vibe", "professional")

    if not niche:
        return HttpResponse(_error_html("Please enter your niche or what you do."))

    name_line = f"Name/brand: {name}." if name else ""
    cta_line = f"Link-in-bio CTA: {cta}." if cta else ""
    system = (
        "You are a social media growth expert specialising in Instagram profiles. "
        "Write compelling Instagram bios that instantly communicate who you are, what you do, and what followers gain. "
        "Each bio MUST be under 150 characters. Use emojis strategically. "
        "Output exactly 3 numbered bio options, each on its own line."
    )
    user = (
        f"{name_line} Niche: {niche}. "
        f"Values/personality: {values or 'not specified'}. "
        f"Vibe: {vibe}. {cta_line}\n\n"
        "Write 3 Instagram bio options, each under 150 characters."
    )
    try:
        result = groq_chat(system, user, max_tokens=400, temperature=0.9)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "insta-bio-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 14. Social Media Post Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def social_media_post_generator(request):
    platform = request.POST.get("platform", "instagram")
    topic = request.POST.get("topic", "").strip()
    goal = request.POST.get("goal", "engagement")
    tone = request.POST.get("tone", "casual")

    if not topic:
        return HttpResponse(_error_html("Please describe what the post is about."))

    char_limits = {
        "instagram": "2,200 characters max, use emojis and line breaks",
        "twitter": "280 characters max, punchy and direct",
        "linkedin": "1,300 characters, professional tone, value-driven",
        "facebook": "500 characters, conversational and community-focused",
        "tiktok": "150 characters caption, casual and trendy",
    }
    limit_note = char_limits.get(platform, "appropriate length for the platform")
    system = (
        "You are a social media strategist who writes viral, high-engagement posts. "
        f"Write for {platform}. Respect: {limit_note}. "
        "Include relevant emojis, a hook in the first line, and a clear call to action. "
        "Output the full post, then suggest 5 hashtags on a separate line."
    )
    user = f"Write a {tone} {platform} post to drive {goal} about: {topic}"
    try:
        result = groq_chat(system, user, max_tokens=600, temperature=0.85)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "social-post-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 15. LinkedIn Headline Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def linkedin_headline_generator(request):
    role = request.POST.get("role", "").strip()
    industry = request.POST.get("industry", "").strip()
    skills = request.POST.get("skills", "").strip()
    goal = request.POST.get("goal", "").strip()

    if not role:
        return HttpResponse(_error_html("Please enter your current role or job title."))

    system = (
        "You are a LinkedIn optimization expert and personal branding coach. "
        "Write magnetic LinkedIn headlines that attract recruiters and opportunities. "
        "Headlines must be under 220 characters. Lead with value, not just a job title. "
        "Use the | separator between sections. Output exactly 5 numbered headline options."
    )
    user = (
        f"Current role: {role}.\n"
        f"Industry: {industry or 'not specified'}.\n"
        f"Key skills: {skills or 'not specified'}.\n"
        f"Career goal: {goal or 'not specified'}.\n\n"
        "Write 5 LinkedIn headline options, each under 220 characters."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.85)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "linkedin-headline-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 16. Job Description Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def job_description_generator(request):
    job_title = request.POST.get("job_title", "").strip()
    company = request.POST.get("company", "").strip()
    level = request.POST.get("level", "mid-level")
    responsibilities = request.POST.get("responsibilities", "").strip()
    skills = request.POST.get("skills", "").strip()
    location = request.POST.get("location", "").strip()

    if not job_title:
        return HttpResponse(_error_html("Please enter a job title."))

    system = (
        "You are an expert HR professional and inclusive hiring specialist. "
        "Write clear, compelling, bias-free job descriptions that attract top talent. "
        "Structure: Role Overview (2–3 sentences), Key Responsibilities (6–8 bullet points), "
        "Requirements (must-haves), Nice to Have, What We Offer. "
        "Use inclusive language. Avoid gendered words and unnecessary degree requirements."
    )
    user = (
        f"Job title: {job_title}\n"
        f"Company: {company or 'our company'}\n"
        f"Level: {level}\n"
        f"Key responsibilities: {responsibilities or 'standard for this role'}\n"
        f"Required skills: {skills or 'standard for this role'}\n"
        f"Location/work type: {location or 'not specified'}\n\n"
        "Write a complete, inclusive job description."
    )
    try:
        result = groq_chat(system, user, max_tokens=1200)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "job-desc-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 17. Privacy Policy Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def privacy_policy_generator(request):
    site_name = request.POST.get("site_name", "").strip()
    site_url = request.POST.get("site_url", "").strip()
    data_collected = request.POST.get("data_collected", "").strip()
    contact_email = request.POST.get("contact_email", "").strip()
    jurisdiction = request.POST.get("jurisdiction", "GDPR + CCPA")

    if not site_name:
        return HttpResponse(_error_html("Please enter your website or app name."))

    system = (
        "You are a legal document specialist. Write clear, comprehensive privacy policies "
        "that comply with GDPR, CCPA, and general international standards. "
        "Include all standard sections: Introduction, Data Collected, How We Use Data, "
        "Data Sharing, Cookies, User Rights, Data Retention, Security, Children's Privacy, "
        "Changes to Policy, Contact Information. Write in plain English, not legalese."
    )
    user = (
        f"Website/App name: {site_name}\n"
        f"Website URL: {site_url or 'not provided'}\n"
        f"Data collected: {data_collected or 'name, email, usage data'}\n"
        f"Contact email: {contact_email or '[your contact email]'}\n"
        f"Jurisdiction compliance: {jurisdiction}\n\n"
        "Generate a complete privacy policy."
    )
    try:
        result = groq_chat(system, user, max_tokens=2000, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "privacy-policy-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 18. Terms & Conditions Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def terms_conditions_generator(request):
    site_name = request.POST.get("site_name", "").strip()
    site_url = request.POST.get("site_url", "").strip()
    business_type = request.POST.get("business_type", "SaaS / web application")
    contact_email = request.POST.get("contact_email", "").strip()
    jurisdiction = request.POST.get("jurisdiction", "")

    if not site_name:
        return HttpResponse(_error_html("Please enter your website or app name."))

    system = (
        "You are a legal document specialist. Write clear, enforceable Terms and Conditions "
        "in plain English. Include all standard sections: Acceptance of Terms, Use License, "
        "Prohibited Activities, Disclaimer of Warranties, Limitation of Liability, "
        "User Accounts, Intellectual Property, Termination, Governing Law, Changes to Terms, Contact. "
        "Write accessibly — avoid unnecessary legalese."
    )
    user = (
        f"Website/App name: {site_name}\n"
        f"URL: {site_url or 'not provided'}\n"
        f"Business type: {business_type}\n"
        f"Contact email: {contact_email or '[your contact email]'}\n"
        f"Governing law/jurisdiction: {jurisdiction or 'not specified'}\n\n"
        "Generate complete Terms and Conditions."
    )
    try:
        result = groq_chat(system, user, max_tokens=2000, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "terms-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 19. Resignation Letter Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def resignation_letter_generator(request):
    your_name = request.POST.get("your_name", "").strip()
    manager_name = request.POST.get("manager_name", "").strip()
    company = request.POST.get("company", "").strip()
    last_day = request.POST.get("last_day", "").strip()
    reason = request.POST.get("reason", "").strip()
    tone = request.POST.get("tone", "professional")

    if not company:
        return HttpResponse(_error_html("Please enter the company name."))

    name_line = f"Employee name: {your_name}." if your_name else ""
    manager_line = f"Manager's name: {manager_name}." if manager_name else ""
    reason_line = f"Reason for leaving: {reason}." if reason else ""
    system = (
        "You are an expert HR professional. Write professional, gracious resignation letters "
        "that maintain good relationships and leave a positive impression. "
        "Include: date, recipient, formal opening, statement of resignation with last day, "
        "brief gratitude for the opportunity, offer to help with transition, warm closing."
    )
    user = (
        f"{name_line} {manager_line} Company: {company}. "
        f"Last working day: {last_day or 'two weeks from today'}. "
        f"{reason_line} Tone: {tone}.\n\nWrite the resignation letter."
    )
    try:
        result = groq_chat(system, user, max_tokens=700)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "resignation-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 20. NDA Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def nda_generator(request):
    disclosing_party = request.POST.get("disclosing_party", "").strip()
    receiving_party = request.POST.get("receiving_party", "").strip()
    purpose = request.POST.get("purpose", "").strip()
    duration = request.POST.get("duration", "2 years")
    nda_type = request.POST.get("nda_type", "one-way")
    jurisdiction = request.POST.get("jurisdiction", "").strip()

    if not disclosing_party or not receiving_party:
        return HttpResponse(_error_html("Please enter both party names."))

    system = (
        "You are a legal document specialist. Write clear, enforceable Non-Disclosure Agreements. "
        "Include: parties, recitals/purpose, definition of confidential information, obligations, "
        "exclusions from confidentiality, permitted disclosures, term and termination, "
        "remedies, governing law, entire agreement clause, signature blocks. "
        "Write in plain, professional English."
    )
    user = (
        f"NDA type: {nda_type} (one-way = only receiving party bound; mutual = both parties bound)\n"
        f"Disclosing party: {disclosing_party}\n"
        f"Receiving party: {receiving_party}\n"
        f"Purpose of disclosure: {purpose or 'business discussions and potential partnership'}\n"
        f"Confidentiality duration: {duration}\n"
        f"Governing law: {jurisdiction or '[Jurisdiction to be filled in]'}\n\n"
        "Generate a complete NDA."
    )
    try:
        result = groq_chat(system, user, max_tokens=2000, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "nda-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 21. Cookie Policy Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def cookie_policy_generator(request):
    site_name = request.POST.get("site_name", "").strip()
    site_url = request.POST.get("site_url", "").strip()
    cookie_types = request.POST.get("cookie_types", "essential, analytics, marketing")
    contact_email = request.POST.get("contact_email", "").strip()
    jurisdiction = request.POST.get("jurisdiction", "GDPR (EU/UK)")

    if not site_name:
        return HttpResponse(_error_html("Please enter your website name."))

    system = (
        "You are a legal document specialist. Write clear, GDPR-compliant cookie policies "
        "in plain English. Include: what cookies are, types used and their purpose, "
        "third-party cookies, how users can manage/opt-out, updates to the policy, contact info. "
        "Use clear headings for each section."
    )
    user = (
        f"Website name: {site_name}\n"
        f"Website URL: {site_url or 'not provided'}\n"
        f"Cookie types used: {cookie_types}\n"
        f"Contact email: {contact_email or '[your contact email]'}\n"
        f"Jurisdiction: {jurisdiction}\n\n"
        "Generate a complete cookie policy."
    )
    try:
        result = groq_chat(system, user, max_tokens=1500, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "cookie-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 22. Disclaimer Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def disclaimer_generator(request):
    site_name = request.POST.get("site_name", "").strip()
    disclaimer_type = request.POST.get("disclaimer_type", "general")
    industry = request.POST.get("industry", "").strip()
    contact_email = request.POST.get("contact_email", "").strip()

    if not site_name:
        return HttpResponse(_error_html("Please enter your website or business name."))

    system = (
        "You are a legal document specialist. Write clear, professional disclaimers that "
        "protect businesses from liability. Use plain language. Tailor content to the "
        "disclaimer type (medical/financial/general/affiliate/fitness). Include: "
        "limitation of liability, no professional advice, accuracy disclaimer, "
        "external links, right to change content, contact info."
    )
    user = (
        f"Website/Business name: {site_name}\n"
        f"Disclaimer type: {disclaimer_type}\n"
        f"Industry/niche: {industry or 'general'}\n"
        f"Contact email: {contact_email or '[your contact email]'}\n\n"
        "Generate a complete disclaimer."
    )
    try:
        result = groq_chat(system, user, max_tokens=1000, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "disclaimer-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 23. Article Rewriter
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def article_rewriter(request):
    article = request.POST.get("article", "").strip()
    style = request.POST.get("style", "match original tone")
    goal = request.POST.get("goal", "uniqueness and clarity")

    if not article:
        return HttpResponse(_error_html("Please paste the article to rewrite."))
    if len(article) > 10000:
        article = article[:10000]

    system = (
        "You are an expert content editor. Rewrite articles to be unique and engaging "
        "while preserving the original meaning and key facts. Vary sentence structure, "
        "use active voice, improve flow and readability. Do not add new facts or remove "
        "important information."
    )
    user = (
        f"Style: {style}. Goal: {goal}.\n\n"
        f"ORIGINAL ARTICLE:\n{article}\n\n"
        "Provide the fully rewritten version:"
    )
    try:
        result = groq_chat(system, user, max_tokens=2000, temperature=0.75)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_markdown_result_html(result, "article-rewriter-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 24. Resume Summary Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def resume_summary_generator(request):
    job_title = request.POST.get("job_title", "").strip()
    years_exp = request.POST.get("years_exp", "").strip()
    skills = request.POST.get("skills", "").strip()
    achievement = request.POST.get("achievement", "").strip()
    target_role = request.POST.get("target_role", "").strip()

    if not job_title:
        return HttpResponse(_error_html("Please enter your job title."))

    system = (
        "You are an expert resume writer and career coach. Write compelling professional "
        "summary statements (3–4 sentences, 50–80 words) for resumes. Focus on value "
        "delivered, key skills, and career goals. Make it specific, achievement-oriented, "
        "and ATS-friendly. Generate 3 different versions."
    )
    user = (
        f"Current/most recent role: {job_title}\n"
        f"Years of experience: {years_exp or 'not specified'}\n"
        f"Key skills: {skills or 'standard for the role'}\n"
        f"Key achievement: {achievement or 'not specified'}\n"
        f"Target role: {target_role or 'similar to current'}\n\n"
        "Write 3 strong resume professional summary options."
    )
    try:
        result = groq_chat(system, user, max_tokens=700, temperature=0.75)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "resume-summary-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 25. Resume Bullet Point Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def resume_bullet_generator(request):
    job_title = request.POST.get("job_title", "").strip()
    responsibility = request.POST.get("responsibility", "").strip()
    achievement = request.POST.get("achievement", "").strip()
    industry = request.POST.get("industry", "").strip()

    if not job_title or not responsibility:
        return HttpResponse(_error_html("Please enter your job title and a responsibility."))

    system = (
        "You are an expert resume writer. Transform job duties into powerful, quantifiable "
        "resume bullet points. Start each with a strong action verb. Include metrics where "
        "possible. Use CAR (Challenge–Action–Result) or PAR format. "
        "Write for ATS optimization — be specific and keyword-rich."
    )
    user = (
        f"Job title: {job_title}\n"
        f"Industry: {industry or 'not specified'}\n"
        f"Responsibility/task: {responsibility}\n"
        f"Achievement or result: {achievement or 'improve as appropriate'}\n\n"
        "Generate 5 strong resume bullet points for this responsibility."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.7)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "resume-bullet-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 26. Interview Question Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def interview_question_generator(request):
    job_title = request.POST.get("job_title", "").strip()
    level = request.POST.get("level", "mid-level")
    skills = request.POST.get("skills", "").strip()
    question_type = request.POST.get("question_type", "mixed (behavioral + technical + situational)")

    if not job_title:
        return HttpResponse(_error_html("Please enter a job title."))

    system = (
        "You are an expert HR professional and hiring manager. Generate insightful interview "
        "questions that reveal candidates' skills, experience, and problem-solving ability. "
        "For each question, add a brief 'Look for:' note on what makes a strong answer. "
        "Format: Q: [question]\nLook for: [key signals]\n"
    )
    user = (
        f"Job title: {job_title}\n"
        f"Seniority level: {level}\n"
        f"Key skills/requirements: {skills or 'standard for this role'}\n"
        f"Question type preference: {question_type}\n\n"
        "Generate 10 strong interview questions with interviewer notes."
    )
    try:
        result = groq_chat(system, user, max_tokens=1200, temperature=0.7)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "interview-questions-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 27. AI Business Name Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_business_name_generator(request):
    description = request.POST.get("description", "").strip()
    industry = request.POST.get("industry", "").strip()
    style = request.POST.get("style", "modern and professional")
    keywords = request.POST.get("keywords", "").strip()

    if not description:
        return HttpResponse(_error_html("Please describe your business."))

    keywords_line = f"Keywords to consider: {keywords}." if keywords else ""
    system = (
        "You are a branding expert and creative naming specialist. Generate memorable, "
        "unique business names that are: easy to pronounce and spell, domain-friendly "
        "(ideally .com available), reflect the brand values, and stand out. "
        "For each name provide: name, a 1-line rationale, domain tip. "
        "Generate 10 business name ideas."
    )
    user = (
        f"Business description: {description}\n"
        f"Industry: {industry or 'not specified'}\n"
        f"Naming style: {style}\n"
        f"{keywords_line}\n\n"
        "Generate 10 unique business name ideas with rationale."
    )
    try:
        result = groq_chat(system, user, max_tokens=800, temperature=0.9)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "business-name-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 28. AI FAQ Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def ai_faq_generator(request):
    topic = request.POST.get("topic", "").strip()
    audience = request.POST.get("audience", "").strip()
    num_faqs = request.POST.get("num_faqs", "8")
    context = request.POST.get("context", "").strip()

    if not topic:
        return HttpResponse(_error_html("Please enter a topic or product."))

    context_line = f"Additional context: {context}." if context else ""
    system = (
        "You are an SEO expert and content strategist. Generate FAQs that target real "
        "search queries (People Also Ask), are concise and helpful, and are structured "
        "for Google featured snippets. Each answer should be 2–4 sentences. "
        "Format: Q: [question]\nA: [answer]\n"
    )
    user = (
        f"Topic/product/service: {topic}\n"
        f"Target audience: {audience or 'general audience'}\n"
        f"{context_line}\n\n"
        f"Generate {num_faqs} SEO-optimized FAQ questions and answers."
    )
    try:
        result = groq_chat(system, user, max_tokens=1400, temperature=0.6)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "faq-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 29. Cold Email Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def cold_email_generator(request):
    offer = request.POST.get("offer", "").strip()
    recipient_role = request.POST.get("recipient_role", "").strip()
    your_name = request.POST.get("your_name", "").strip()
    company = request.POST.get("company", "").strip()
    goal = request.POST.get("goal", "book a call")
    tone = request.POST.get("tone", "professional and direct")

    if not offer:
        return HttpResponse(_error_html("Please describe what you're offering."))

    system = (
        "You are a sales copywriter expert in cold outreach. Write cold emails that: "
        "are under 150 words, lead with the recipient's value not self-promotion, "
        "have a compelling subject line, one clear CTA, and feel human and personalized. "
        "Avoid spam trigger words. Output: Subject: [line]\n\n[email body]"
    )
    user = (
        f"Sender: {your_name or '[Your Name]'} from {company or '[Your Company]'}\n"
        f"Recipient role: {recipient_role or 'decision maker'}\n"
        f"What you're offering: {offer}\n"
        f"Goal of the email: {goal}\n"
        f"Tone: {tone}\n\n"
        "Write a compelling cold email with subject line."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.8)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "cold-email-result"))


# ─────────────────────────────────────────────────────────────────────────────
# 30. YouTube Title Generator
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def youtube_title_generator(request):
    topic = request.POST.get("topic", "").strip()
    video_type = request.POST.get("video_type", "tutorial")
    keyword = request.POST.get("keyword", "").strip()
    audience = request.POST.get("audience", "").strip()

    if not topic:
        return HttpResponse(_error_html("Please enter your video topic."))

    keyword_line = f"Target keyword: {keyword}." if keyword else ""
    audience_line = f"Target audience: {audience}." if audience else ""
    system = (
        "You are a YouTube SEO expert. Generate video titles that are click-worthy, "
        "under 70 characters, include the target keyword naturally, use proven formulas "
        "(How to, X Ways, Why, The Truth About, etc.), and rank well in YouTube search. "
        "Generate 10 title options numbered 1–10."
    )
    user = (
        f"Video topic: {topic}\n"
        f"Video type: {video_type}\n"
        f"{keyword_line} {audience_line}\n\n"
        "Generate 10 compelling YouTube title options."
    )
    try:
        result = groq_chat(system, user, max_tokens=400, temperature=0.9)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "youtube-title-result"))


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher map (tool_slug → handler)
# ─────────────────────────────────────────────────────────────────────────────
AI_HANDLERS = {
    # Batch 1
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
    # Batch 2
    "ai-content-generator": ai_content_generator,
    "ai-essay-generator": ai_essay_generator,
    "instagram-bio-generator": instagram_bio_generator,
    "social-media-post-generator": social_media_post_generator,
    "linkedin-headline-generator": linkedin_headline_generator,
    "job-description-generator": job_description_generator,
    "privacy-policy-generator": privacy_policy_generator,
    "terms-and-conditions-generator": terms_conditions_generator,
    "resignation-letter-generator": resignation_letter_generator,
    "nda-generator": nda_generator,
    # Batch 3
    "cookie-policy-generator": cookie_policy_generator,
    "disclaimer-generator": disclaimer_generator,
    "article-rewriter": article_rewriter,
    "resume-summary-generator": resume_summary_generator,
    "resume-bullet-generator": resume_bullet_generator,
    "interview-question-generator": interview_question_generator,
    "ai-business-name-generator": ai_business_name_generator,
    "ai-faq-generator": ai_faq_generator,
    "cold-email-generator": cold_email_generator,
    "youtube-title-generator": youtube_title_generator,
}
