"""
Central registry of all tool categories and tools.
Each tool entry drives URL generation, sitemap, homepage cards, and SEO metadata.
"""

CATEGORIES = [
    {
        "slug": "calculators",
        "name": "Calculators",
        "description": "Math, finance, health, and science calculators.",
        "icon": "🧮",
        "tools": [
            {"slug": "age-calculator", "name": "Age Calculator", "description": "Calculate exact age from a birth date."},
            {"slug": "bmi-calculator", "name": "BMI Calculator", "description": "Calculate Body Mass Index from height and weight."},
            {"slug": "compound-interest-calculator", "name": "Compound Interest Calculator", "description": "Calculate compound interest with monthly/yearly breakdown."},
            {"slug": "percentage-calculator", "name": "Percentage Calculator", "description": "Find percentage, percentage change, and percentage of a number."},
            {"slug": "loan-calculator", "name": "Loan Calculator", "description": "Monthly payment, total interest, and amortisation schedule."},
            {"slug": "tip-calculator", "name": "Tip Calculator", "description": "Calculate tip and split bills between multiple people."},
            {"slug": "calorie-calculator", "name": "Calorie Calculator", "description": "Daily calorie needs based on age, weight, and activity level."},
            {"slug": "mortgage-calculator", "name": "Mortgage Calculator", "description": "Monthly mortgage payment and amortisation schedule."},
            {"slug": "bac-calculator", "name": "BAC Calculator", "description": "Estimate blood alcohol content from drinks and time."},
            {"slug": "scientific-calculator", "name": "Scientific Calculator", "description": "Full scientific calculator with trig, log, and exponent functions."},
        ],
    },
    {
        "slug": "converters",
        "name": "Converters",
        "description": "Unit, format, and data converters.",
        "icon": "🔄",
        "tools": [
            {"slug": "length-converter", "name": "Length Converter", "description": "Convert between meters, feet, inches, km, miles, and more."},
            {"slug": "weight-converter", "name": "Weight Converter", "description": "Convert between kg, lbs, oz, grams, and more."},
            {"slug": "temperature-converter", "name": "Temperature Converter", "description": "Convert Celsius, Fahrenheit, and Kelvin."},
            {"slug": "currency-converter", "name": "Currency Converter", "description": "Live exchange rates for 170+ currencies."},
            {"slug": "data-storage-converter", "name": "Data Storage Converter", "description": "Convert KB, MB, GB, TB, and more."},
            {"slug": "speed-converter", "name": "Speed Converter", "description": "Convert mph, km/h, m/s, and knots."},
            {"slug": "time-zone-converter", "name": "Time Zone Converter", "description": "Convert times between any two time zones."},
            {"slug": "binary-converter", "name": "Binary Converter", "description": "Convert between binary, decimal, hex, and octal."},
        ],
    },
    {
        "slug": "pdf",
        "name": "PDF Tools",
        "description": "Merge, split, compress, convert, and edit PDF files.",
        "icon": "📄",
        "tools": [
            {"slug": "merge-pdf", "name": "Merge PDF", "description": "Combine multiple PDF files into one."},
            {"slug": "compress-pdf", "name": "Compress PDF", "description": "Reduce PDF file size without losing quality."},
            {"slug": "pdf-to-word", "name": "PDF to Word", "description": "Convert PDF documents to editable Word files."},
            {"slug": "jpg-to-pdf", "name": "JPG to PDF", "description": "Convert JPG images to a PDF document."},
            {"slug": "split-pdf", "name": "Split PDF", "description": "Split a PDF into individual pages or ranges."},
            {"slug": "rotate-pdf", "name": "Rotate PDF", "description": "Rotate PDF pages 90, 180, or 270 degrees."},
            {"slug": "add-watermark-to-pdf", "name": "Add Watermark to PDF", "description": "Stamp text or image watermarks on PDF pages."},
            {"slug": "encrypt-pdf", "name": "Encrypt PDF", "description": "Password-protect a PDF file."},
            {"slug": "decrypt-pdf", "name": "Decrypt PDF", "description": "Remove password protection from a PDF."},
        ],
    },
    {
        "slug": "image",
        "name": "Image Tools",
        "description": "Resize, compress, convert, and edit images online.",
        "icon": "🖼️",
        "tools": [
            {"slug": "image-resizer", "name": "Image Resizer", "description": "Resize images to any dimension online."},
            {"slug": "image-compressor", "name": "Image Compressor", "description": "Compress JPG, PNG, and WebP without visible quality loss."},
            {"slug": "background-remover", "name": "Background Remover", "description": "Remove image backgrounds automatically."},
            {"slug": "image-converter", "name": "Image Converter", "description": "Convert between JPG, PNG, WebP, GIF, and more."},
            {"slug": "image-cropper", "name": "Image Cropper", "description": "Crop images to any size or aspect ratio."},
            {"slug": "add-text-to-image", "name": "Add Text to Image", "description": "Add custom text overlays to any image."},
            {"slug": "image-color-picker", "name": "Image Color Picker", "description": "Extract hex color codes from any image."},
            {"slug": "heic-to-jpg", "name": "HEIC to JPG", "description": "Convert iPhone HEIC photos to JPG."},
        ],
    },
    {
        "slug": "video",
        "name": "Video Tools",
        "description": "Compress, convert, trim, and edit video files.",
        "icon": "🎬",
        "tools": [
            {"slug": "compress-mp4", "name": "Compress MP4", "description": "Reduce MP4 video file size online."},
            {"slug": "mp4-to-mp3", "name": "MP4 to MP3", "description": "Extract audio from video files."},
            {"slug": "trim-video", "name": "Trim Video", "description": "Cut and trim video files online."},
            {"slug": "convert-video", "name": "Video Converter", "description": "Convert between MP4, AVI, MOV, WebM, and more."},
            {"slug": "gif-maker", "name": "GIF Maker", "description": "Create GIFs from video clips online."},
        ],
    },
    {
        "slug": "audio",
        "name": "Audio Tools",
        "description": "Convert, compress, trim, and edit audio files.",
        "icon": "🎵",
        "tools": [
            {"slug": "mp3-converter", "name": "MP3 Converter", "description": "Convert audio files to MP3 format."},
            {"slug": "audio-trimmer", "name": "Audio Trimmer", "description": "Cut and trim audio files online."},
            {"slug": "audio-compressor", "name": "Audio Compressor", "description": "Reduce audio file size without quality loss."},
            {"slug": "audio-to-text", "name": "Audio to Text", "description": "Transcribe speech from audio files."},
        ],
    },
    {
        "slug": "text",
        "name": "Text Tools",
        "description": "Word count, case converter, text generators, and more.",
        "icon": "📝",
        "tools": [
            {"slug": "word-counter", "name": "Word Counter", "description": "Count words, characters, sentences, and paragraphs."},
            {"slug": "case-converter", "name": "Case Converter", "description": "Convert text to uppercase, lowercase, title case, camelCase, and more."},
            {"slug": "lorem-ipsum-generator", "name": "Lorem Ipsum Generator", "description": "Generate placeholder lorem ipsum text."},
            {"slug": "remove-duplicate-lines", "name": "Remove Duplicate Lines", "description": "Remove duplicate lines from text instantly."},
            {"slug": "text-to-speech", "name": "Text to Speech", "description": "Convert text to audio using browser TTS."},
            {"slug": "slug-generator", "name": "Slug Generator", "description": "Generate URL-friendly slugs from any text."},
            {"slug": "word-frequency-analyzer", "name": "Word Frequency Analyzer", "description": "Analyse how often each word appears in text."},
            {"slug": "paraphrasing-tool", "name": "Paraphrasing Tool", "description": "Rewrite any text in a different style while keeping the original meaning.", "ai": True},
            {"slug": "article-rewriter", "name": "Article Rewriter", "description": "Rewrite full articles to be unique and plagiarism-free with AI.", "ai": True},
        ],
    },
    {
        "slug": "developer",
        "name": "Developer Tools",
        "description": "JSON, regex, encoders, formatters, and API tools.",
        "icon": "💻",
        "tools": [
            {"slug": "json-formatter", "name": "JSON Formatter", "description": "Format, validate, and minify JSON data."},
            {"slug": "base64-encoder", "name": "Base64 Encoder / Decoder", "description": "Encode and decode Base64 strings."},
            {"slug": "url-encoder", "name": "URL Encoder / Decoder", "description": "Encode and decode URL components."},
            {"slug": "html-encoder", "name": "HTML Encoder / Decoder", "description": "Encode and decode HTML entities."},
            {"slug": "regex-tester", "name": "Regex Tester", "description": "Test and debug regular expressions live."},
            {"slug": "diff-checker", "name": "Diff Checker", "description": "Compare two blocks of text and highlight differences."},
            {"slug": "css-minifier", "name": "CSS Minifier", "description": "Minify CSS for faster page loads."},
            {"slug": "javascript-minifier", "name": "JavaScript Minifier", "description": "Minify JavaScript code online."},
            {"slug": "markdown-editor", "name": "Markdown Editor", "description": "Write and preview Markdown with live rendering."},
            {"slug": "jwt-decoder", "name": "JWT Decoder", "description": "Decode and inspect JSON Web Tokens."},
            {"slug": "cron-expression-generator", "name": "Cron Expression Generator", "description": "Build and validate cron schedule expressions."},
        ],
    },
    {
        "slug": "security",
        "name": "Security Tools",
        "description": "Password generators, hash tools, and encryption utilities.",
        "icon": "🔐",
        "tools": [
            {"slug": "password-generator", "name": "Password Generator", "description": "Generate strong, random passwords instantly."},
            {"slug": "password-strength-checker", "name": "Password Strength Checker", "description": "Check how strong your password is."},
            {"slug": "uuid-generator", "name": "UUID Generator", "description": "Generate random UUIDs (v1, v4)."},
            {"slug": "md5-generator", "name": "MD5 Generator", "description": "Generate MD5 hashes from any string."},
            {"slug": "sha-generator", "name": "SHA Generator", "description": "Generate SHA-1, SHA-256, and SHA-512 hashes."},
            {"slug": "bcrypt-generator", "name": "BCrypt Generator", "description": "Hash and verify passwords using BCrypt."},
            {"slug": "ssl-checker", "name": "SSL Certificate Checker", "description": "Check SSL certificate validity and expiry."},
        ],
    },
    {
        "slug": "network",
        "name": "Network Tools",
        "description": "DNS lookup, IP tools, WHOIS, and HTTP checkers.",
        "icon": "🌐",
        "tools": [
            {"slug": "dns-lookup", "name": "DNS Lookup", "description": "Query DNS records for any domain."},
            {"slug": "ip-lookup", "name": "IP Lookup", "description": "Get geolocation and info for any IP address."},
            {"slug": "whois-lookup", "name": "WHOIS Lookup", "description": "Look up domain registration details."},
            {"slug": "http-status-checker", "name": "HTTP Status Checker", "description": "Check the HTTP status code for any URL."},
            {"slug": "open-port-checker", "name": "Open Port Checker", "description": "Check if a port is open on any host."},
        ],
    },
    {
        "slug": "seo",
        "name": "SEO Tools",
        "description": "Meta tags, schema, sitemap, and SEO checkers.",
        "icon": "📈",
        "tools": [
            {"slug": "meta-tag-generator", "name": "Meta Tag Generator", "description": "Generate SEO meta tags for any page."},
            {"slug": "schema-markup-generator", "name": "Schema Markup Generator", "description": "Generate JSON-LD schema markup for rich results."},
            {"slug": "robots-txt-generator", "name": "Robots.txt Generator", "description": "Create a robots.txt file for your website."},
            {"slug": "serp-preview", "name": "SERP Preview Tool", "description": "Preview how your page looks in Google search results."},
            {"slug": "xml-sitemap-generator", "name": "XML Sitemap Generator", "description": "Generate an XML sitemap for any website."},
            {"slug": "opengraph-generator", "name": "Open Graph Generator", "description": "Generate Open Graph meta tags for social sharing."},
        ],
    },
    {
        "slug": "color",
        "name": "Color Tools",
        "description": "Color pickers, palette generators, and converters.",
        "icon": "🎨",
        "tools": [
            {"slug": "color-picker", "name": "Color Picker", "description": "Pick colors and get hex, RGB, and HSL values."},
            {"slug": "hex-to-rgb", "name": "Hex to RGB Converter", "description": "Convert hex color codes to RGB values."},
            {"slug": "palette-generator", "name": "Palette Generator", "description": "Generate harmonious color palettes."},
            {"slug": "gradient-generator", "name": "Gradient Generator", "description": "Create CSS linear and radial gradients."},
        ],
    },
    {
        "slug": "qr-barcode",
        "name": "QR & Barcode",
        "description": "Generate and scan QR codes and barcodes.",
        "icon": "📱",
        "tools": [
            {"slug": "qr-code-generator", "name": "QR Code Generator", "description": "Generate QR codes for URLs, text, WiFi, vCards, and more."},
            {"slug": "qr-code-reader", "name": "QR Code Reader", "description": "Scan and decode QR codes from images."},
            {"slug": "barcode-generator", "name": "Barcode Generator", "description": "Generate Code128, EAN, UPC, and ISBN barcodes."},
            {"slug": "barcode-reader", "name": "Barcode Reader", "description": "Read and decode barcodes from images."},
        ],
    },
    {
        "slug": "document",
        "name": "Document Generators",
        "description": "Letter, contract, policy, and certificate generators.",
        "icon": "📋",
        "tools": [
            {"slug": "privacy-policy-generator", "name": "Privacy Policy Generator", "description": "Generate a GDPR & CCPA-compliant privacy policy with AI.", "ai": True},
            {"slug": "terms-and-conditions-generator", "name": "Terms & Conditions Generator", "description": "Generate terms and conditions for your website with AI.", "ai": True},
            {"slug": "cookie-policy-generator", "name": "Cookie Policy Generator", "description": "Generate a GDPR-compliant cookie policy for your website with AI.", "ai": True},
            {"slug": "disclaimer-generator", "name": "Disclaimer Generator", "description": "Generate a professional disclaimer for your website or app with AI.", "ai": True},
            {"slug": "nda-generator", "name": "NDA Generator", "description": "Generate a non-disclosure agreement with AI.", "ai": True},
            {"slug": "resignation-letter-generator", "name": "Resignation Letter Generator", "description": "Generate a professional resignation letter with AI.", "ai": True},
            {"slug": "cover-letter-generator", "name": "Cover Letter Generator", "description": "Generate a tailored cover letter for job applications.", "ai": True},
        ],
    },
    {
        "slug": "invoice",
        "name": "Invoice & Receipt",
        "description": "Free invoice, receipt, and billing document generators.",
        "icon": "🧾",
        "tools": [
            {"slug": "invoice-generator", "name": "Invoice Generator", "description": "Create professional invoices and download as PDF."},
            {"slug": "receipt-generator", "name": "Receipt Generator", "description": "Generate payment receipts instantly."},
            {"slug": "estimate-generator", "name": "Estimate Generator", "description": "Create job estimates and quotes."},
        ],
    },
    {
        "slug": "resume",
        "name": "Resume & HR",
        "description": "Resume builders, ATS checkers, and HR letter generators.",
        "icon": "👔",
        "tools": [
            {"slug": "resume-builder", "name": "Resume Builder", "description": "Build a professional resume online."},
            {"slug": "ats-resume-checker", "name": "ATS Resume Checker", "description": "Check if your resume passes ATS filters.", "ai": True},
            {"slug": "cover-letter-generator", "name": "Cover Letter Generator", "description": "Generate tailored cover letters.", "ai": True},
            {"slug": "job-description-generator", "name": "Job Description Generator", "description": "Write clear, inclusive job descriptions with AI.", "ai": True},
            {"slug": "resume-summary-generator", "name": "Resume Summary Generator", "description": "Generate 3 powerful resume professional summary options with AI.", "ai": True},
            {"slug": "resume-bullet-generator", "name": "Resume Bullet Point Generator", "description": "Transform job duties into powerful, quantifiable resume bullets with AI.", "ai": True},
            {"slug": "interview-question-generator", "name": "Interview Question Generator", "description": "Generate 10 tailored interview questions with interviewer notes.", "ai": True},
        ],
    },
    {
        "slug": "social-media",
        "name": "Social Media Tools",
        "description": "Caption generators, hashtag tools, and social media utilities.",
        "icon": "📲",
        "tools": [
            {"slug": "hashtag-generator", "name": "Hashtag Generator", "description": "Generate relevant hashtags for Instagram, Twitter, and TikTok.", "ai": True},
            {"slug": "instagram-bio-generator", "name": "Instagram Bio Generator", "description": "Write a compelling Instagram bio with AI.", "ai": True},
            {"slug": "social-media-post-generator", "name": "Social Media Post Generator", "description": "Generate engaging posts for any platform with AI.", "ai": True},
            {"slug": "linkedin-headline-generator", "name": "LinkedIn Headline Generator", "description": "Write a magnetic LinkedIn headline that attracts recruiters.", "ai": True},
            {"slug": "youtube-thumbnail-maker", "name": "YouTube Thumbnail Maker", "description": "Create eye-catching YouTube thumbnails."},
            {"slug": "youtube-title-generator", "name": "YouTube Title Generator", "description": "Generate 10 click-worthy, SEO-optimized YouTube video titles with AI.", "ai": True},
        ],
    },
    {
        "slug": "ecommerce",
        "name": "eCommerce Tools",
        "description": "Amazon, eBay, Etsy fee calculators and product tools.",
        "icon": "🛒",
        "tools": [
            {"slug": "amazon-fee-calculator", "name": "Amazon Fee Calculator", "description": "Calculate Amazon FBA and FBM fees."},
            {"slug": "profit-margin-calculator", "name": "Profit Margin Calculator", "description": "Calculate gross and net profit margins."},
            {"slug": "shipping-cost-calculator", "name": "Shipping Cost Calculator", "description": "Estimate international shipping costs."},
            {"slug": "product-description-generator", "name": "Product Description Generator", "description": "Write compelling product descriptions."},
        ],
    },
    {
        "slug": "random",
        "name": "Random Generators",
        "description": "Random number, name, password, and fake data generators.",
        "icon": "🎲",
        "tools": [
            {"slug": "random-number-generator", "name": "Random Number Generator", "description": "Generate random numbers in any range."},
            {"slug": "random-name-generator", "name": "Random Name Generator", "description": "Generate random names for testing or games."},
            {"slug": "random-password-generator", "name": "Random Password Generator", "description": "Generate cryptographically random passwords."},
            {"slug": "random-picker", "name": "Random Picker", "description": "Pick a random item from a list."},
            {"slug": "lorem-ipsum-generator", "name": "Lorem Ipsum Generator", "description": "Generate placeholder lorem ipsum text."},
        ],
    },
    {
        "slug": "date-time",
        "name": "Date & Time",
        "description": "Date calculators, timezone tools, and countdowns.",
        "icon": "📅",
        "tools": [
            {"slug": "date-calculator", "name": "Date Calculator", "description": "Calculate days between two dates."},
            {"slug": "epoch-converter", "name": "Epoch Converter", "description": "Convert Unix timestamps to human-readable dates."},
            {"slug": "timezone-converter", "name": "Time Zone Converter", "description": "Convert times between any two time zones."},
            {"slug": "countdown-timer", "name": "Countdown Timer", "description": "Create a countdown timer to any date."},
            {"slug": "age-calculator", "name": "Age Calculator", "description": "Calculate exact age from a date of birth."},
        ],
    },
    {
        "slug": "ai",
        "name": "AI Tools",
        "description": "AI-powered generators, writers, and assistants.",
        "icon": "🤖",
        "tools": [
            {"slug": "ai-grammar-checker", "name": "AI Grammar Checker", "description": "Check and correct grammar, spelling, and style with AI.", "ai": True},
            {"slug": "ai-summarizer", "name": "AI Summarizer", "description": "Summarize long articles and documents with AI in seconds.", "ai": True},
            {"slug": "ai-email-generator", "name": "AI Email Generator", "description": "Write professional emails instantly with AI.", "ai": True},
            {"slug": "ai-code-generator", "name": "AI Code Generator", "description": "Generate clean code from natural language descriptions.", "ai": True},
            {"slug": "ai-meta-description-generator", "name": "AI Meta Description Generator", "description": "Generate click-worthy SEO meta descriptions with AI.", "ai": True},
            {"slug": "ai-content-generator", "name": "AI Content Generator", "description": "Generate blog posts, articles, and web copy with AI.", "ai": True},
            {"slug": "ai-essay-generator", "name": "AI Essay Generator", "description": "Generate well-structured essays on any topic with AI.", "ai": True},
            {"slug": "ai-business-name-generator", "name": "AI Business Name Generator", "description": "Generate 10 memorable, domain-friendly business names with AI.", "ai": True},
            {"slug": "ai-faq-generator", "name": "AI FAQ Generator", "description": "Generate SEO-optimized FAQ questions and answers for any topic.", "ai": True},
            {"slug": "cold-email-generator", "name": "Cold Email Generator", "description": "Write high-converting cold emails with subject line and CTA with AI.", "ai": True},
        ],
    },
]


def get_all_tools():
    """Flat list of (category, tool) tuples for sitemap etc."""
    result = []
    for cat in CATEGORIES:
        for tool in cat["tools"]:
            result.append((cat, tool))
    return result


def get_category(slug):
    return next((c for c in CATEGORIES if c["slug"] == slug), None)


def get_tool(category_slug, tool_slug):
    cat = get_category(category_slug)
    if not cat:
        return None, None
    tool = next((t for t in cat["tools"] if t["slug"] == tool_slug), None)
    return cat, tool
