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
# Batch 4 — Tools 31–40
# ─────────────────────────────────────────────────────────────────────────────

@require_POST
def etsy_product_description_generator(request):
    product_name = request.POST.get("product_name", "").strip()
    product_type = request.POST.get("product_type", "").strip()
    materials = request.POST.get("materials", "").strip()
    target_buyer = request.POST.get("target_buyer", "").strip()
    keywords = request.POST.get("keywords", "").strip()

    if not product_name:
        return HttpResponse(_error_html("Please enter your product name."))

    materials_line = f"Materials / made from: {materials}." if materials else ""
    buyer_line = f"Target buyer: {target_buyer}." if target_buyer else ""
    keywords_line = f"Keywords to include naturally: {keywords}." if keywords else ""
    type_line = f"Product type / category: {product_type}." if product_type else ""
    system = (
        "You are an expert Etsy seller and copywriter. Write Etsy listings that are "
        "SEO-optimized, warm, and story-driven. Etsy buyers want to feel the human "
        "connection. Include keyword-rich title (under 130 chars), a compelling "
        "description (3–4 short paragraphs), and exactly 13 comma-separated tags "
        "(Etsy allows 13). Format: TITLE: ... / DESCRIPTION: ... / TAGS: ..."
    )
    user = (
        f"Product: {product_name}\n"
        f"{type_line} {materials_line} {buyer_line} {keywords_line}\n\n"
        "Write the full Etsy listing."
    )
    try:
        result = groq_chat(system, user, max_tokens=700, temperature=0.75)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "etsy-result"))


@require_POST
def news_article_summarizer(request):
    article = request.POST.get("article", "").strip()
    num_points = request.POST.get("num_points", "5")
    include_tldr = request.POST.get("include_tldr", "yes")

    if not article:
        return HttpResponse(_error_html("Please paste the article text."))
    if len(article) > 12000:
        article = article[:12000]

    tldr_line = "Start with a one-sentence TL;DR on its own line before the bullets." if include_tldr == "yes" else ""
    system = (
        "You are a professional news editor. Summarise articles into clear, factual "
        "bullet points. Preserve key facts, names, numbers, and quotes. Be concise — "
        "each bullet under 25 words. No opinion, no padding."
    )
    user = (
        f"{tldr_line}\n\n"
        f"Summarise the following article into {num_points} bullet points:\n\n"
        f"{article}"
    )
    try:
        result = groq_chat(system, user, max_tokens=600, temperature=0.3)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "news-summary-result"))


@require_POST
def product_review_generator(request):
    product_name = request.POST.get("product_name", "").strip()
    rating = request.POST.get("rating", "5")
    pros = request.POST.get("pros", "").strip()
    cons = request.POST.get("cons", "").strip()
    use_case = request.POST.get("use_case", "").strip()
    tone = request.POST.get("tone", "honest and balanced")

    if not product_name:
        return HttpResponse(_error_html("Please enter a product name."))

    pros_line = f"Positives to mention: {pros}." if pros else ""
    cons_line = f"Negatives / limitations: {cons}." if cons else ""
    use_line = f"How I use it: {use_case}." if use_case else ""
    system = (
        "You are a verified buyer writing an authentic product review. Write in a "
        "natural, conversational first-person voice. Avoid sounding like marketing copy. "
        "Include a title line, a rating line, and 2–3 paragraphs. Sound genuine."
    )
    user = (
        f"Product: {product_name}\n"
        f"Star rating: {rating}/5\n"
        f"Tone: {tone}\n"
        f"{pros_line} {cons_line} {use_line}\n\n"
        "Write the review."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.8)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "review-result"))


@require_POST
def ai_business_plan_generator(request):
    business_idea = request.POST.get("business_idea", "").strip()
    industry = request.POST.get("industry", "").strip()
    target_market = request.POST.get("target_market", "").strip()
    revenue_model = request.POST.get("revenue_model", "").strip()

    if not business_idea:
        return HttpResponse(_error_html("Please describe your business idea."))

    industry_line = f"Industry: {industry}." if industry else ""
    market_line = f"Target market: {target_market}." if target_market else ""
    revenue_line = f"Revenue model: {revenue_model}." if revenue_model else ""
    system = (
        "You are a seasoned business consultant and startup advisor. Write concise, "
        "structured one-page business plans using markdown. Include: ## Executive Summary, "
        "## Problem & Solution, ## Target Market, ## Revenue Model, ## Key Competitors, "
        "## Go-to-Market Strategy, ## Key Metrics to Track. Be specific, not generic."
    )
    user = (
        f"Business idea: {business_idea}\n"
        f"{industry_line} {market_line} {revenue_line}\n\n"
        "Write a one-page business plan."
    )
    try:
        result = groq_chat(system, user, max_tokens=1200, temperature=0.6)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_markdown_result_html(result, "business-plan-result"))


@require_POST
def ai_press_release_generator(request):
    headline = request.POST.get("headline", "").strip()
    company = request.POST.get("company", "").strip()
    announcement = request.POST.get("announcement", "").strip()
    quote = request.POST.get("quote", "").strip()
    contact = request.POST.get("contact", "").strip()

    if not headline:
        return HttpResponse(_error_html("Please enter the press release headline."))

    quote_line = f'Include this quote: "{quote}"' if quote else ""
    contact_line = f"Contact info for boilerplate: {contact}." if contact else ""
    company_line = f"Company name: {company}." if company else ""
    system = (
        "You are a PR professional. Write press releases in standard AP Style format: "
        "FOR IMMEDIATE RELEASE, dateline, lead paragraph (who/what/when/where/why), "
        "body paragraphs, quote, boilerplate, ### end marker. Professional tone."
    )
    user = (
        f"Headline: {headline}\n"
        f"{company_line}\n"
        f"Announcement details: {announcement}\n"
        f"{quote_line} {contact_line}\n\n"
        "Write the full press release."
    )
    try:
        result = groq_chat(system, user, max_tokens=900, temperature=0.5)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "press-release-result"))


@require_POST
def linkedin_summary_generator(request):
    job_title = request.POST.get("job_title", "").strip()
    skills = request.POST.get("skills", "").strip()
    achievement = request.POST.get("achievement", "").strip()
    goal = request.POST.get("goal", "").strip()
    tone = request.POST.get("tone", "professional and approachable")

    if not job_title:
        return HttpResponse(_error_html("Please enter your job title."))

    skills_line = f"Key skills: {skills}." if skills else ""
    achievement_line = f"Top achievement: {achievement}." if achievement else ""
    goal_line = f"Career goal / what I'm open to: {goal}." if goal else ""
    system = (
        "You are a LinkedIn profile expert and personal brand coach. Write LinkedIn About "
        "sections (summaries) that are authentic, keyword-rich, and tell a compelling story. "
        "3–4 short paragraphs, first-person, ends with a soft CTA. 200–300 words. "
        "Generate 2 versions: one shorter (150 words) and one fuller (280 words)."
    )
    user = (
        f"Role: {job_title}\n"
        f"Tone: {tone}\n"
        f"{skills_line} {achievement_line} {goal_line}\n\n"
        "Write 2 LinkedIn summary options."
    )
    try:
        result = groq_chat(system, user, max_tokens=800, temperature=0.75)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "linkedin-summary-result"))


@require_POST
def twitter_bio_generator(request):
    profession = request.POST.get("profession", "").strip()
    keywords = request.POST.get("keywords", "").strip()
    vibe = request.POST.get("vibe", "professional")
    cta = request.POST.get("cta", "").strip()

    if not profession:
        return HttpResponse(_error_html("Please enter your profession or what you do."))

    keywords_line = f"Keywords / interests to include: {keywords}." if keywords else ""
    cta_line = f"End with this CTA or link mention: {cta}." if cta else ""
    system = (
        "You are a Twitter/X profile expert. Write Twitter bios under 160 characters — "
        "punchy, memorable, and personality-driven. Each bio should be on its own numbered "
        "line. Include emoji where they add value. Generate 5 bio options."
    )
    user = (
        f"What I do: {profession}\n"
        f"Vibe/tone: {vibe}\n"
        f"{keywords_line} {cta_line}\n\n"
        "Generate 5 Twitter bio options (each under 160 characters)."
    )
    try:
        result = groq_chat(system, user, max_tokens=350, temperature=0.9)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "twitter-bio-result"))


@require_POST
def salary_negotiation_email(request):
    current_salary = request.POST.get("current_salary", "").strip()
    desired_salary = request.POST.get("desired_salary", "").strip()
    offer = request.POST.get("offer", "").strip()
    company = request.POST.get("company", "").strip()
    reason = request.POST.get("reason", "").strip()

    if not desired_salary:
        return HttpResponse(_error_html("Please enter your desired salary."))

    current_line = f"Current salary: {current_salary}." if current_salary else ""
    offer_line = f"Offer received: {offer}." if offer else ""
    company_line = f"Company: {company}." if company else ""
    reason_line = f"Key reasons for ask: {reason}." if reason else ""
    system = (
        "You are a career coach specialising in salary negotiation. Write professional, "
        "confident negotiation emails that are warm, not aggressive. Lead with enthusiasm "
        "for the role, state the ask clearly, justify with 1–2 data points, and end "
        "collaboratively. Under 200 words."
    )
    user = (
        f"Desired salary: {desired_salary}\n"
        f"{current_line} {offer_line} {company_line} {reason_line}\n\n"
        "Write the salary negotiation email with subject line."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.6)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "salary-email-result"))


@require_POST
def thank_you_email_generator(request):
    recipient = request.POST.get("recipient", "").strip()
    context = request.POST.get("context", "job interview")
    key_points = request.POST.get("key_points", "").strip()
    tone = request.POST.get("tone", "professional and warm")

    if not recipient:
        return HttpResponse(_error_html("Please enter the recipient's name or role."))

    points_line = f"Specific things to mention or reference: {key_points}." if key_points else ""
    system = (
        "You are a professional communications expert. Write genuine, concise thank-you "
        "emails that feel personal — not templated. Include a subject line, opening, "
        "body (2–3 sentences), and warm close. Under 150 words."
    )
    user = (
        f"Recipient: {recipient}\n"
        f"Context: {context}\n"
        f"Tone: {tone}\n"
        f"{points_line}\n\n"
        "Write the thank-you email with subject line."
    )
    try:
        result = groq_chat(system, user, max_tokens=400, temperature=0.75)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "thankyou-email-result"))


@require_POST
def tagline_generator(request):
    brand_name = request.POST.get("brand_name", "").strip()
    industry = request.POST.get("industry", "").strip()
    value_prop = request.POST.get("value_prop", "").strip()
    tone = request.POST.get("tone", "bold and memorable")

    if not brand_name:
        return HttpResponse(_error_html("Please enter your brand name."))

    industry_line = f"Industry: {industry}." if industry else ""
    value_line = f"Core value proposition: {value_prop}." if value_prop else ""
    system = (
        "You are a world-class brand strategist and copywriter. Generate memorable taglines "
        "and slogans — under 8 words each, punchy, distinct. Mix styles: benefit-driven, "
        "emotional, aspirational, witty. Number each one 1–10."
    )
    user = (
        f"Brand: {brand_name}\n"
        f"Tone: {tone}\n"
        f"{industry_line} {value_line}\n\n"
        "Generate 10 tagline / slogan options."
    )
    try:
        result = groq_chat(system, user, max_tokens=400, temperature=0.95)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "tagline-result"))


# ─────────────────────────────────────────────────────────────────────────────
# Batch 5 — Tools 41–50
# ─────────────────────────────────────────────────────────────────────────────

@require_POST
def ai_story_generator(request):
    genre = request.POST.get("genre", "").strip()
    protagonist = request.POST.get("protagonist", "").strip()
    setting = request.POST.get("setting", "").strip()
    length = request.POST.get("length", "short")

    if not genre:
        return HttpResponse(_error_html("Please enter a story genre."))

    length_map = {"short": "400–600 words", "medium": "700–1000 words", "long": "1200–1600 words"}
    word_count = length_map.get(length, "400–600 words")
    protagonist_line = f"Main character: {protagonist}." if protagonist else ""
    setting_line = f"Setting: {setting}." if setting else ""

    system = (
        "You are a skilled fiction author. Write compelling, original short stories with "
        "vivid descriptions, natural dialogue, and satisfying story arcs. "
        "Include an engaging hook, rising tension, and a clear ending. "
        "Write in prose — no bullet points, no headers. Just the story."
    )
    user = (
        f"Genre: {genre}\n"
        f"{protagonist_line} {setting_line}\n"
        f"Length: approximately {word_count}\n\n"
        "Write the complete story."
    )
    try:
        result = groq_chat(system, user, max_tokens=1400, temperature=0.92)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "story-result"))


@require_POST
def ai_paragraph_generator(request):
    topic = request.POST.get("topic", "").strip()
    tone = request.POST.get("tone", "informative")
    length = request.POST.get("length", "medium")

    if not topic:
        return HttpResponse(_error_html("Please enter a topic."))

    length_map = {
        "short": "3–4 sentences (50–70 words)",
        "medium": "5–7 sentences (80–120 words)",
        "long": "8–10 sentences (150–200 words)",
    }
    word_count = length_map.get(length, "5–7 sentences")

    system = (
        "You are an expert writer. Generate well-crafted paragraphs on any topic. "
        "Each paragraph should have a clear topic sentence, supporting details, and a "
        "closing sentence. Output 3 different paragraph options, each clearly labeled "
        "Option 1, Option 2, Option 3. Vary the angle or emphasis in each option."
    )
    user = (
        f"Topic: {topic}\n"
        f"Tone: {tone}\n"
        f"Length: {word_count}\n\n"
        "Generate 3 paragraph options."
    )
    try:
        result = groq_chat(system, user, max_tokens=800, temperature=0.8)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "paragraph-result"))


@require_POST
def sentence_rewriter(request):
    sentence = request.POST.get("sentence", "").strip()
    style = request.POST.get("style", "clear and natural")
    num_variations = request.POST.get("num_variations", "5")

    if not sentence:
        return HttpResponse(_error_html("Please enter a sentence to rewrite."))
    if len(sentence) > 1000:
        return HttpResponse(_error_html("Please keep the input under 1,000 characters."))

    system = (
        "You are an expert writing assistant. Rewrite sentences in different ways while "
        "preserving the exact meaning. Each variation should feel distinct — vary sentence "
        "structure, word choice, and emphasis. Never change the core meaning."
    )
    user = (
        f"Style / tone goal: {style}\n"
        f"Original sentence: {sentence}\n\n"
        f"Write {num_variations} rewritten versions, numbered."
    )
    try:
        result = groq_chat(system, user, max_tokens=600, temperature=0.82)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "sentence-rewriter-result"))


@require_POST
def ai_prompt_generator(request):
    goal = request.POST.get("goal", "").strip()
    ai_tool = request.POST.get("ai_tool", "ChatGPT")
    output_format = request.POST.get("output_format", "")

    if not goal:
        return HttpResponse(_error_html("Please describe what you want to accomplish."))

    format_line = f"Desired output format: {output_format}." if output_format else ""
    system = (
        "You are an expert prompt engineer. Write optimised prompts for AI tools that "
        "are clear, specific, and get consistently great results. Use proven techniques: "
        "role assignment, context, constraints, output format instructions. "
        "Generate 5 prompt variations from simple to detailed. Number each one."
    )
    user = (
        f"AI tool: {ai_tool}\n"
        f"Goal / task: {goal}\n"
        f"{format_line}\n\n"
        "Generate 5 optimised prompt options, from brief to detailed."
    )
    try:
        result = groq_chat(system, user, max_tokens=800, temperature=0.8)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "prompt-result"))


@require_POST
def chatgpt_prompt_generator(request):
    goal = request.POST.get("goal", "").strip()
    persona = request.POST.get("persona", "")
    output_format = request.POST.get("output_format", "")
    context = request.POST.get("context", "").strip()

    if not goal:
        return HttpResponse(_error_html("Please describe what you want ChatGPT to do."))

    persona_line = f"Act as: {persona}." if persona else ""
    format_line = f"Output format: {output_format}." if output_format else ""
    context_line = f"Context / background: {context}." if context else ""
    system = (
        "You are a ChatGPT prompt engineering expert. Write highly effective ChatGPT prompts "
        "that get detailed, accurate, high-quality responses. Use best practices: assign a role, "
        "provide context, set constraints, specify format. Generate 3 prompt options: "
        "Option 1 — concise, Option 2 — detailed, Option 3 — chain-of-thought approach."
    )
    user = (
        f"Goal: {goal}\n"
        f"{persona_line} {format_line} {context_line}\n\n"
        "Write 3 ChatGPT prompt options."
    )
    try:
        result = groq_chat(system, user, max_tokens=700, temperature=0.78)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "chatgpt-prompt-result"))


@require_POST
def instagram_caption_generator(request):
    post_topic = request.POST.get("post_topic", "").strip()
    tone = request.POST.get("tone", "casual and engaging")
    include_hashtags = request.POST.get("include_hashtags", "yes")
    cta = request.POST.get("cta", "").strip()

    if not post_topic:
        return HttpResponse(_error_html("Please describe your post."))

    hashtag_line = "Add 5–8 relevant hashtags at the end." if include_hashtags == "yes" else "Do not include hashtags."
    cta_line = f"Include this call to action: {cta}." if cta else "Add a natural call to action."
    system = (
        "You are a social media copywriter specialising in Instagram. Write captions that "
        "stop the scroll — hook in the first line, engaging body, and clear CTA. "
        "Use line breaks for readability. Include emojis naturally. "
        "Generate 3 caption options labeled Option 1, Option 2, Option 3. "
        "Vary the opening angle and length."
    )
    user = (
        f"Post topic / description: {post_topic}\n"
        f"Tone: {tone}\n"
        f"{cta_line} {hashtag_line}\n\n"
        "Write 3 Instagram caption options."
    )
    try:
        result = groq_chat(system, user, max_tokens=700, temperature=0.88)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "ig-caption-result"))


@require_POST
def ai_quiz_generator(request):
    topic = request.POST.get("topic", "").strip()
    num_questions = request.POST.get("num_questions", "5")
    difficulty = request.POST.get("difficulty", "medium")
    quiz_type = request.POST.get("quiz_type", "multiple choice")

    if not topic:
        return HttpResponse(_error_html("Please enter a quiz topic."))

    system = (
        "You are an expert educator and quiz designer. Create engaging, accurate quizzes. "
        "For multiple choice: provide question, 4 options (A/B/C/D), and mark the correct answer. "
        "For true/false: provide question and answer. "
        "For open-ended: provide question and a model answer. "
        "Number each question. Make questions clear, unambiguous, and educational."
    )
    user = (
        f"Topic: {topic}\n"
        f"Number of questions: {num_questions}\n"
        f"Difficulty: {difficulty}\n"
        f"Quiz type: {quiz_type}\n\n"
        f"Generate {num_questions} quiz questions with answers."
    )
    try:
        result = groq_chat(system, user, max_tokens=1200, temperature=0.5)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "quiz-result"))


@require_POST
def ai_blog_intro_generator(request):
    blog_title = request.POST.get("blog_title", "").strip()
    audience = request.POST.get("audience", "").strip()
    tone = request.POST.get("tone", "informative and engaging")
    keyword = request.POST.get("keyword", "").strip()

    if not blog_title:
        return HttpResponse(_error_html("Please enter your blog title or topic."))

    audience_line = f"Target audience: {audience}." if audience else ""
    keyword_line = f"Include the keyword '{keyword}' naturally in the intro." if keyword else ""
    system = (
        "You are an expert blog writer and content strategist. Write blog introductions that "
        "hook readers immediately and keep them reading. Use proven techniques: "
        "start with a question, surprising stat, bold claim, or relatable scenario. "
        "Each intro should be 80–120 words and end by previewing what the article covers. "
        "Generate 2 introduction options."
    )
    user = (
        f"Blog title / topic: {blog_title}\n"
        f"Tone: {tone}\n"
        f"{audience_line} {keyword_line}\n\n"
        "Write 2 blog introduction options."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.82)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "blog-intro-result"))


@require_POST
def tweet_generator(request):
    topic = request.POST.get("topic", "").strip()
    tone = request.POST.get("tone", "informative")
    include_hashtags = request.POST.get("include_hashtags", "yes")
    tweet_type = request.POST.get("tweet_type", "single tweet")

    if not topic:
        return HttpResponse(_error_html("Please enter what the tweet is about."))

    hashtag_line = "End with 1–2 relevant hashtags." if include_hashtags == "yes" else "No hashtags."
    thread_line = "Write as a 5-tweet thread (number each tweet 1/5, 2/5 etc.)." if tweet_type == "thread" else "Write 5 single tweet options."
    system = (
        "You are a Twitter/X copywriter who creates viral, engaging tweets. "
        "Each tweet must be under 280 characters. Lead with a hook. "
        "Make every word count — no filler. Use active voice. "
        f"{thread_line}"
    )
    user = (
        f"Topic: {topic}\n"
        f"Tone: {tone}\n"
        f"{hashtag_line}\n\n"
        "Generate the tweets."
    )
    try:
        result = groq_chat(system, user, max_tokens=500, temperature=0.88)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "tweet-result"))


@require_POST
def youtube_description_generator(request):
    video_title = request.POST.get("video_title", "").strip()
    summary = request.POST.get("summary", "").strip()
    keywords = request.POST.get("keywords", "").strip()
    include_timestamps = request.POST.get("include_timestamps", "no")

    if not video_title:
        return HttpResponse(_error_html("Please enter your video title."))

    keywords_line = f"Target keywords to include: {keywords}." if keywords else ""
    timestamps_line = "Include a sample timestamps section (00:00 Intro, etc.)." if include_timestamps == "yes" else ""
    system = (
        "You are a YouTube SEO expert. Write YouTube video descriptions that rank in search "
        "and keep viewers engaged. Structure: hook paragraph (2–3 sentences), expanded "
        "description (what viewers will learn), chapters/timestamps if requested, "
        "social links placeholder, keywords naturally in the text. "
        "Aim for 200–300 words total. SEO-optimised but natural to read."
    )
    user = (
        f"Video title: {video_title}\n"
        f"Video summary: {summary or 'not provided — infer from title'}\n"
        f"{keywords_line} {timestamps_line}\n\n"
        "Write the complete YouTube description."
    )
    try:
        result = groq_chat(system, user, max_tokens=600, temperature=0.7)
    except Exception:
        return HttpResponse(_error_html())
    return HttpResponse(_result_html(result, "yt-desc-result"))


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
    # Batch 4
    "etsy-product-description-generator": etsy_product_description_generator,
    # Batch 5
    "ai-story-generator": ai_story_generator,
    "ai-paragraph-generator": ai_paragraph_generator,
    "sentence-rewriter": sentence_rewriter,
    "ai-prompt-generator": ai_prompt_generator,
    "chatgpt-prompt-generator": chatgpt_prompt_generator,
    "instagram-caption-generator": instagram_caption_generator,
    "ai-quiz-generator": ai_quiz_generator,
    "ai-blog-intro-generator": ai_blog_intro_generator,
    "tweet-generator": tweet_generator,
    "youtube-description-generator": youtube_description_generator,
    "news-article-summarizer": news_article_summarizer,
    "product-review-generator": product_review_generator,
    "ai-business-plan-generator": ai_business_plan_generator,
    "ai-press-release-generator": ai_press_release_generator,
    "linkedin-summary-generator": linkedin_summary_generator,
    "twitter-bio-generator": twitter_bio_generator,
    "salary-negotiation-email": salary_negotiation_email,
    "thank-you-email-generator": thank_you_email_generator,
    "tagline-generator": tagline_generator,
}
