# ROOT404 product vision (design, not implementation status)

The original Arabic product design is retained below. Descriptions are target behavior, not release claims. Roadmap checklists are aspirations; current delivery and evidence are in ../FEATURE_COMPLETION_MATRIX.md. No production verification is implied. The former README architecture snapshot is replaced by ../ARCHITECTURE.md, which separates running components from intended integrations.

> **Planned product design — not a delivered capability.**

## 📌 الفكرة العامة ورؤية النظام

تعتمد منصة **École 1337** على بيئة تعلم ذاتية وتنافسية (Peer-to-Peer & Gamified Learning) تحاكي روح **École 42** بأسلوب مُعرّب ومكيّف لواقع المبرمج التونسي:

| الميزة | الوصف |
|---|---|
| 🧪 **Moulinette صارمة** | فحص تلقائي للكود على مستوى الـ Norme، تسريبات الذاكرة (Memory Leaks)، وحالات الاختبار |
| 🔐 **أمان متقدم** | توثيق بمرمز زمني مؤقت عبر البريد (Email OTP) + نظام مكافحة غش ذكي (Anti-Cheating Bot) |
| 🪙 **اقتصاد داخلي** | رموز تقدم (Jetons d'avance) ورصيد حساب تقدّم (Valeur de compte) |
| 📦 **حاويات معزولة** | تنفيذ كل مشروع داخل Docker Container بنظام Ubuntu مستقل |
| 🌍 **مسارات متعددة** | دعم 5 لغات أساسية ومستويات صعوبة متدرجة مع خوارزميات متقدمة |

---

> **Planned product design — not a delivered capability.**

## 🚀 ما الذي يميّز École 1337؟

هذا هو الجزء الجديد الذي يقرّب المنصة أكثر من فلسفة 42 الأصلية، مع لمسة عصرية بالذكاء الاصطناعي:

> **Planned product design — not a delivered capability.**

### 🕳️ نظام Black Hole والمسار الزمني

بدل نظام تسجيل تقليدي، كل طالب يدخل بـ **"عداد بقاء" (Survival Timer)**:

- كل مسار (Path) له مدة زمنية معيّنة لإتمامه والوصول لمستوى معيّن (مثلاً 3 أشهر للوصول للـ Level 5).
- إذا تجاوز الطالب المدة بدون تقدّم كافٍ، يدخل في **"منطقة الخطر" (Warning Zone)** يتوصل فيها بتنبيهات والمساعد الذكي يقترح خطة تدارك.
- عدم التقدم يؤدي لتفعيل **Black Hole**: تجميد الحساب مؤقتًا وإعادة توزيع الأولوية للطلبة النشيطين — تمامًا كما في 42 الحقيقية، لكن بمرونة أكبر ونظام إنذار مسبق بالذكاء الاصطناعي بدل المفاجأة الكاملة.

> **Planned product design — not a delivered capability.**

### 👥 نظام Peer-to-Peer Evaluation (تصحيح بين الطلبة)

بالتوازي مع الـ Moulinette الآلية، نضيف طبقة تصحيح بشرية حقيقية:

- بعد اجتياز مشروع الـ Moulinette آليًا، يُطلب من الطالب **حجز جلسة تصحيح (Correction Slot)** مع طالب آخر وصل لنفس المستوى أو أعلى.
- كل جلسة توثّق عبر **Video/Chat Room مدمج** داخل المنصة (WebRTC) مع Checklist تفاعلي يظهره النظام تلقائيًا حسب المشروع.
- الطالب المُصحِّح يكسب **نقاط تصحيح (Correction Points)** إضافية إلى جانب رصيده العادي، ما يشجع الطلبة المتقدمين على البقاء نشيطين ومساعدة غيرهم.
- نظام تقييم ثنائي الاتجاه: الطالب يقيّم جودة التصحيح، والمصحِّح يقيّم جدية الطالب — يغذّي هذا **"مؤشر السمعة" (Reputation Score)** الظاهر على البروفايل.

> **Planned product design — not a delivered capability.**

### 🏘️ نظام Coalitions (التحالفات)

كما في 42، الطلبة يُقسّمون تلقائيًا (أو باختيارهم) إلى **تحالفات/بيوت (Coalitions)** بألوان وهويات مختلفة:

- كل تحالف يجمع نقاط من إنجازات أعضائه (مشاريع منجزة، تصحيحات، مساهمات في تحديات جماعية).
- **لوحة ترتيب تحالفات** منفصلة عن الترتيب الفردي، تُحدّث أسبوعيًا.
- فعاليات دورية (Coalition Wars): تحديات برمجية جماعية بمهلة 48 ساعة، تحاكي "Hackathons" داخلية.

> **Planned product design — not a delivered capability.**

### 🤖 المساعد الذكي كموجّه وليس كحلّال

لضمان روح "التعلّم الذاتي" الأصيلة في 42، المساعد الذكي **AI Assistant** مُقيَّد بقواعد صارمة:

- لا يعطي الحل النهائي مباشرة، بل يطرح أسئلة موجِّهة (Socratic Hints) ويشرح المفاهيم فقط.
- يحلّل الأخطاء الشائعة في كود الطالب ويقترح موارد تعليمية (لا حلول جاهزة).
- عند اكتشاف نمط "نسخ-لصق" مشبوه، يُبلّغ نظام Anti-Cheating تلقائيًا.

> **Planned product design — not a delivered capability.**

### 🏆 نظام المستويات المرن (Level System)

مقياس مستويات مستمر من **0.00 إلى 21.00** (بالضبط كما في 42)، حيث:
- كل مشروع يضيف نسبة مئوية من مستوى معيّن حسب الصعوبة ونقاط التصحيح.
- شارات إنجاز مرئية (Badges) تُعرض على البروفايل العام والـ Leaderboard.

---

> **Planned product design — not a delivered capability.**

## 🧠 أساليب ومحتويات متقدمة (Advanced Systems)

> **Planned product design — not a delivered capability.**

### 🏊 نظام Piscine (المعسكر التمهيدي المكثّف)

قبل الدخول للمسار الرئيسي، كل طالب جديد يمرّ بـ **Piscine** — معسكر تمهيدي مكثّف يحاكي فلسفة القبول في 42:

- مدة 4 أسابيع، تمارين يومية تتصاعد صعوبتها تدريجيًا (من أساسيات المنطق البرمجي إلى مشروع جماعي ختامي).
- تقييم يومي آلي + تصحيح ند-للند إجباري لكل تمرين.
- **مؤشر ثبات الأداء (Consistency Score)**: لا يكفي حل التمارين، بل الحفاظ على انتظام يومي — ينعكس على معايير القبول النهائي.
- في نهاية الـ Piscine، يُحسب **معدّل قبول** مبني على: نسبة الإنجاز، جودة الكود (Norme)، ونشاط التصحيح.

> **Planned product design — not a delivered capability.**

### 🎯 محرك توصية المسار (Adaptive Path Engine)

بدل مسار ثابت للجميع، نظام توصية ذكي يبني مسارًا شخصيًا لكل طالب:

- يحلل نقاط القوة/الضعف من نتائج الـ Piscine ومشاريع البداية (خوارزميات، بنى معطيات، أنظمة، ويب...).
- يقترح ترتيب مشاريع مخصص، ويعيد التوصية ديناميكيًا كل ما أنهى الطالب مشروعًا جديدًا.
- يكتشف "الفجوات المعرفية" (Knowledge Gaps) ويقترح تمارين تقوية قصيرة قبل مشروع صعب.

> **Planned product design — not a delivered capability.**

### 🧩 مكتبة تحديات متقدمة (Advanced Challenge Library)

طبقة محتوى إضافية فوق المسارات الأساسية:

| الفئة | أمثلة محتوى |
|---|---|
| **Algorithmic Dojo** | تحديات خوارزميات تنافسية بنمط Competitive Programming (شبيهة بـ Codeforces) مع مؤقت وترتيب مباشر |
| **System Design Labs** | تمارين تصميم أنظمة (Load Balancing, Caching, Microservices) بمخططات تفاعلية |
| **Security CTF Track** | تحديات أمن معلوماتي (Capture The Flag) بمستويات Web, Crypto, Reverse Engineering |
| **AI/ML Bootcamp Track** | مسار متقدم في تعلّم الآلة يُبنى فوق أساسيات Python، بمشاريع تدريجية (من Regression إلى Mini-LLM) |
| **Open Source Contributions** | مهام حقيقية من مشاريع مفتوحة المصدر مرتبطة عبر GitHub API، تُقيَّم كمشاريع معتمدة |

> **Planned product design — not a delivered capability.**

### 📊 لوحة تحليلات متقدمة (Advanced Analytics Dashboard)

لوحة بيانات شخصية لكل طالب مبنية على تحليل سلوكي حقيقي:

- **خريطة حرارية للنشاط** (Activity Heatmap) شبيهة بـ GitHub Contributions.
- **تحليل زمن الحل** (Time-to-Solve Trends) لكل نوع مشروع، لمقارنة تطور الطالب عبر الزمن.
- **توقع الإنجاز** (Completion Forecast): تقدير ذكي لتاريخ إنهاء المسار الحالي بناءً على وتيرة التقدم.
- تقرير أسبوعي آلي يُرسل بالبريد يلخّص التقدم، نقاط التصحيح، وترتيب التحالف.

> **Planned product design — not a delivered capability.**

### 🛡️ طبقة أمان وموثوقية متقدمة

- **Sandbox Hardening**: عزل كل حاوية Docker بحدود صارمة على CPU/RAM/Network (لا اتصال إنترنت خارجي أثناء التنفيذ) لمنع أي استغلال.
- **Code Fingerprinting**: مقارنة تشابه الكود بين تسليمات الطلبة (Plagiarism Detection) عبر تحليل AST وليس نصًا خامًا، لتفادي الإيجابيات الخاطئة.
- **Audit Trail كامل**: تسجيل كل عملية حسّاسة (تسليم، تصحيح، تعديل نقاط) في سجل غير قابل للتعديل، لضمان الشفافية عند النزاعات.
- **Rate Limiting & Abuse Detection** على مستوى الـ API لمنع إغراق نظام الـ Moulinette بطلبات وهمية.

> **Planned product design — not a delivered capability.**

### 🔌 API عام للمطوّرين (Public Developer API)

لفتح المنصة على أدوات وتكاملات خارجية:

- **REST + Webhooks** تتيح لأي طالب ربط إنجازاته بأدوات خارجية (بورتفوليو شخصي، بوت Discord/Telegram للتنبيهات).
- **Public Profile API**: عرض مستوى الطالب، الشارات، وسجل المشاريع كـ Widget قابل للتضمين في مواقع خارجية (شبيه بشارة 42).
- توثيق تفاعلي عبر **Swagger/OpenAPI** مدمج مباشرة من FastAPI.

> **Planned product design — not a delivered capability.**

### 🎮 تعزيز التحفيز (Gamification Layer 2.0)

- **نظام شارات متعدد الطبقات** (Bronze/Silver/Gold/Legendary) لكل فئة إنجاز (سرعة، جودة كود، مساعدة الغير).
- **تحديات موسمية** (Seasonal Events): فعاليات محدودة زمنيًا بمكافآت رموز إضافية.
- **نظام إحالة (Referral System)**: مكافأة الطلبة الذين يجلبون زملاء جدد ينجحون في اجتياز الـ Piscine.

---

> **Planned product design — not a delivered capability.**

### 🧬 نظام Exam Mode (الامتحانات المعزولة)

طبقة تقييم رسمية منفصلة عن المشاريع اليومية، تُستخدم لقياس المستوى الحقيقي:

- **بيئة امتحان مقفلة (Locked-Down Browser/Sandbox)**: تعطيل النسخ/اللصق الخارجي، منع فتح تبويبات أخرى، ومراقبة الكاميرا اختياريًا بموافقة الطالب.
- **تصحيح ند-للند إجباري فور انتهاء الوقت** — لا يمكن مغادرة القاعة الافتراضية قبل تصحيح زميل آخر.
- **بنك أسئلة عشوائي (Randomized Exercise Pool)**: كل طالب يحصل على تركيبة مختلفة من التمارين بنفس مستوى الصعوبة، لمنع الغش الجماعي.
- نتائج الامتحان تُدرج كـ "بوابة" (Gate) إجبارية للانتقال بين مستويات معينة (Circle/Tier).

> **Planned product design — not a delivered capability.**

### 🌐 نظام Campus متعدد الفروع (Multi-Campus Architecture)

تحضيرًا لتوسّع المنصة على مستوى تونس (تونس العاصمة، صفاقس، سوسة...):

- كل "Campus" افتراضي له لوحة ترتيب، تحالفات، وفعاليات خاصة به.
- **Inter-Campus Tournaments**: مسابقات دورية بين الفروع، بنتائج مجمّعة على لوحة وطنية.
- إمكانية "زيارة افتراضية" (Cross-Campus Access) لطالب من فرع لمشاريع/فعاليات فرع آخر.

> **Planned product design — not a delivered capability.**

### 🧑‍🏫 نظام Mentorship المتقدم

طبقة توجيه فوق نظام التصحيح العادي:

- طلبة بمستوى Level ≥ 15 يمكنهم التسجيل كـ **Mentors** رسميين.
- جلسات توجيه مجدولة (Office Hours) عبر تقويم مدمج، منفصلة عن جلسات التصحيح الإلزامية.
- نظام "مسار الإرشاد" (Mentorship Track): تتبّع تقدّم الطلبة الموجَّهين وربطه بمكافآت للمرشد.

> **Planned product design — not a delivered capability.**

### 🏢 بوابة الشركاء والتوظيف (Corporate & Hiring Portal)

جسر بين المنصة وسوق الشغل التونسي:

- **بروفايل توظيف تلقائي**: يُبنى من سجل المشاريع، الشارات، ومستوى الطالب — قابل للمشاركة كرابط عام.
- شركات شريكة يمكنها نشر **تحديات توظيف (Hiring Challenges)** مخصصة، ومتابعة نتائج المتقدمين مباشرة من لوحة تحكم خاصة.
- **معرض الشركاء (Partner Fair)** افتراضي دوري يجمع الطلبة المتقدمين بأصحاب العمل.

> **Planned product design — not a delivered capability.**

### 🔄 محرك Sandbox متعدد اللغات (Polyglot Execution Engine)

توسعة تقنية لدعم تنويع أعمق في التقييم الآلي:

- كل لغة مدعومة لها **Runner Image** مستقل داخل `judge_sandbox/` (مثال: `runner_c.py`, `runner_python.py`, `runner_js.py`)، لضمان عزل التبعيات.
- **Test Case DSL** موحّد (YAML/JSON) يكتب به المُشرفون حالات الاختبار مرة واحدة، ويُترجم تلقائيًا لصيغة كل لغة.
- دعم **Interactive Test Mode**: بعض المشاريع (مثل بناء Shell أو Server) تحتاج تفاعل حي مع stdin/stdout أثناء الفحص، وليس فقط مقارنة مخرجات نهائية.

> **Planned product design — not a delivered capability.**

### 📚 محتوى تعليمي تكميلي (Knowledge Base & Micro-Learning)

- **Wiki تفاعلي** مبني من مساهمات الطلبة أنفسهم (Peer-Written Docs)، يُراجعه فريق إشراف قبل النشر.
- **Micro-Lessons**: فيديوهات قصيرة (3-5 دقائق) مرتبطة مباشرة بكل مشروع، تُقترح تلقائيًا عند تعثّر الطالب أكثر من مرة معينة.
- **Glossary تفاعلي**: قاموس مصطلحات تقنية بالعربية والفرنسية والإنجليزية، مربوط بالكود مباشرة (Hover-to-Define في المحرر).

---


> **Planned product design — not a delivered capability.**

## 🚀 أنظمة ROOT 404 Ultimate

هذه الطبقة توسّع المنصة من Coding Academy إلى **Developer Learning Operating System**:
بيئة واحدة ترافق المبرمج من مرحلة المبتدئ إلى Developer متقدم، ثم Mentor وProfessional.

> **Planned product design — not a delivered capability.**

### 🧭 Code Journey — خريطة رحلة الطالب

كل طالب يمتلك خريطة تطور تفاعلية بدل الاعتماد على أرقام الـDashboard فقط:

```text
                    ROOT 404
                       │
                 ┌─────▼─────┐
                 │ LEVEL 00   │
                 │  Piscine   │
                 └─────┬─────┘
                       │
              ┌────────▼────────┐
              │ C / Programming │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Algorithms      │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Memory / Systems│
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Advanced        │
              └────────┬────────┘
                       │
                       ▼
                  FINAL PROJECT
                       │
                       ▼
                    LEVEL 10+
```

كل مرحلة تعرض:
- المشاريع المكتملة والمشاريع القادمة.
- المهارات المكتسبة.
- XP والـLevel.
- نقاط الضعف والـKnowledge Gaps.
- المشاريع التي أصبحت متاحة بعد تحقيق المتطلبات.
- نسبة التقدم داخل المسار.

> **Planned product design — not a delivered capability.**

### 🧠 Skill Graph — خريطة المهارات

نظام مستقل عن الـLevel يقيس المهارات التقنية الفعلية:

```text
C
├── Variables       95%
├── Pointers        62%
├── Memory          41%
├── Structs         78%
└── Functions       91%

Algorithms
├── Sorting         82%
├── Recursion       48%
├── Complexity      37%
└── Graphs          15%
```

يستخدم النظام نتائج المشاريع، الـMoulinette، الـPeer Review، والـChallenges لبناء ملف مهارات ديناميكي.

إذا اكتشف النظام فجوة معرفية، يقترح Micro-Challenges قبل السماح بالانتقال إلى مشروع يعتمد على تلك المهارة.

> **Planned product design — not a delivered capability.**

### 🤖 AI Mentor 2.0 — الموجّه الذكي

تطوير للمساعد الذكي من مجرد Chatbot إلى **Learning Agent** مرتبط بأنظمة المنصة:

```text
Student
   ↓
Code / Submission
   ↓
Moulinette
   ↓
AI Mentor
   ├── Error Understanding
   ├── Socratic Hint
   ├── Guided Question
   ├── Concept Explanation
   ├── Knowledge Gap Detection
   ├── Exercise Recommendation
   └── Progress Follow-up
```

مستويات المساعدة:
1. Hint أولي.
2. سؤال Socratic.
3. تفسير المفهوم.
4. مثال مبسط غير قابل للنسخ كحل نهائي.
5. اقتراح موارد وتمارين إضافية.

الـAI لا يُسمح له بإعطاء الحل النهائي مباشرة في المشاريع التي تتطلب التعلم الذاتي.

> **Planned product design — not a delivered capability.**

### 🔄 Project Lifecycle Engine

كل مشروع يمر بدورة موحدة:

```text
LOCKED
  ↓
AVAILABLE
  ↓
IN PROGRESS
  ↓
SUBMITTED
  ↓
MOULINETTE
  ↓
PEER REVIEW
  ↓
AI ANALYSIS
  ↓
PASSED
  ↓
UNLOCK NEXT PROJECT
```

يمكن لكل مرحلة تسجيل timestamps ونتائجها لتكوين سجل تعلم قابل للتحليل.

> **Planned product design — not a delivered capability.**

### 🤝 Smart Peer Matchmaking

محرك ذكي لاختيار أفضل Peer Reviewer لكل عملية تصحيح.

يعتمد على:
- مستوى الطالب.
- المشروع المطلوب تصحيحه.
- مستوى المصحح.
- Availability.
- اللغة المفضلة.
- Reputation Score.
- تاريخ التصحيحات السابقة.
- تجنب تكرار نفس الأزواج بشكل مفرط.

الهدف هو تقليل وقت انتظار الـCorrection Slots ورفع جودة الـPeer Review.

> **Planned product design — not a delivered capability.**

### 🎙️ Integrated Collaboration Rooms

تتحول الـRooms إلى مساحة تعاون متكاملة داخل ROOT 404:

```text
💬 Study Room
🧪 Correction Room
👨‍💻 Pair Programming
🏆 Competition Room
🎓 Mentor Room
🔴 Live Coding
```

كل Room يمكن أن تحتوي على:
- Chat.
- Voice/Video.
- Code Editor.
- Shared Terminal.
- Screen Sharing.
- AI Mentor.
- Project Checklist.
- Session Report.

> **Planned product design — not a delivered capability.**

### 🏅 Reputation & Trust System

يتم فصل السمعة عن الـXP حتى لا يكون التقدم التقني هو العامل الوحيد.

```text
REPUTATION
──────────────
Code Quality       92
Peer Reviewer      87
Community          78
Mentorship         91
Reliability        95
```

يمكن فتح أدوار مثل:
- Trusted Reviewer.
- Community Helper.
- Mentor Candidate.
- Official Mentor.

وتدخل جودة التصحيح، الالتزام بالمواعيد، تقييمات الآخرين، والنشاط المجتمعي في الحساب.

> **Planned product design — not a delivered capability.**

### 💰 ROOT Economy — الاقتصاد الداخلي

نظام اقتصاد افتراضي غير Pay-to-Win:

**ROOT XP**
- يمثل التقدم الأكاديمي الحقيقي.
- يؤثر في الـLevel وفتح المسارات.

**ROOT Credits**
- مكافآت اجتماعية واختيارية.
- يمكن استخدامها في عناصر تخصيص الحساب، إنشاء بعض الـRooms، وميزات مجتمعية.

قواعد أساسية:
- لا يمكن شراء Level.
- لا يمكن شراء Score.
- لا يمكن شراء Project Completion.
- لا يمكن شراء نتيجة امتحان.

> **Planned product design — not a delivered capability.**

### 🧑‍💼 Developer Portfolio Generator

كل طالب يمكنه إنشاء Portfolio عام تلقائيًا من نشاطه الحقيقي:

```text
root404.tn/u/username

LEVEL 12.47

Skills
C        █████████░
Python   ███████░░░
Docker   ████████░░
Git      █████████░

Projects
✓ Minishell
✓ Web Server
✓ Algorithms
✓ AI Project

Achievements
🏆 Top 5%
🔥 87 Day Streak
⭐ Trusted Reviewer
```

الـPortfolio يعتمد على بيانات موثقة من المنصة بدل إدخال المهارات يدويًا.

> **Planned product design — not a delivered capability.**

### 🔥 Streak & Anti-Burnout Engine

الـStreak لا يهدف إلى إجبار الطالب على الـGrind.

النظام يراقب:
- مدة الجلسات.
- كثافة المشاريع.
- عدد المحاولات.
- التقدم الأسبوعي.
- فترات الراحة.
- مستوى الإرهاق المحتمل من نمط النشاط.

وعند اكتشاف Workload مرتفع، يقترح AI خطة أخف:

```text
🔥 24 Day Streak

⚠️ High workload detected

Recommendation:
20 min → Pointer Challenge
10 min → Review
Then → Rest
```

> **Planned product design — not a delivered capability.**

### ⚡ Daily Missions

مهمات قصيرة يومية للحفاظ على النشاط:

```text
╔══════════════════════════╗
║      ⚡ DAILY MISSION    ║
╠══════════════════════════╣
║ Reverse a linked list    ║
║                          ║
║ Difficulty: ★★★☆☆        ║
║ Time: ~30 min            ║
║ Reward: +120 XP          ║
╚══════════════════════════╝
```

تتغير المهمات حسب مستوى الطالب والـSkill Graph والـKnowledge Gaps.

> **Planned product design — not a delivered capability.**

### ⚔️ ROOT Arena

منطقة منافسات برمجية مباشرة:

```text
1v1 Coding Battle

Player A
    VS
Player B

Problem:
Binary Search

Time: 15:00

LIVE
```

أنواع المنافسات:
- 1v1.
- Team Battle.
- Speed Coding.
- Algorithm Duel.
- Debugging Battle.

يكون للـArena Leaderboard منفصل حتى لا تختلط المنافسات السريعة مع التقدم الأكاديمي الأساسي.

> **Planned product design — not a delivered capability.**

### 🔬 AI Code Review

بعد الـMoulinette، يقدم النظام تقريرًا تحليليًا:

```text
AUTOMATED REPORT

Correctness       94%
Memory Safety     88%
Code Quality      81%
Complexity        73%
Readability       90%

AI REVIEW

⚠️ Function X is too complex.

💡 Suggested concept:
Separation of Concerns
```

الـAI يشرح المشكلة ويقترح مفهومًا للتعلم، لكنه لا يستبدل الـPeer Review ولا يمنح الموافقة النهائية وحده.

> **Planned product design — not a delivered capability.**

### 🛡️ Integrity / Trust Score

تطوير نظام Anti-Cheating إلى مؤشر سلامة متعدد العوامل:

```text
INTEGRITY SCORE: 96/100

Code Similarity       2%
Typing Pattern        Normal
Submission Pattern    Normal
AI Dependency         Low
Peer Review           Valid
```

عند وجود مؤشر قوي على الغش:

```text
⚠️ REVIEW REQUIRED

Reason:
High similarity with another submission
```

أي قرار عقابي مهم يجب أن يمر عبر Human Review، ولا يعتمد على AI وحده.

> **Planned product design — not a delivered capability.**

### 📊 Student Analytics 360°

إضافة مؤشرات تعلم أكثر عمقًا إلى الـAdvanced Analytics:

**Learning Velocity**
```text
██████████████░░ 78%
```

**Consistency**
```text
████████████████ 91%
```

**Difficulty Tolerance**
```text
Easy       ██████████
Medium     █████████
Hard       ██████
Extreme    ███
```

الـAI يمكنه تحويل البيانات إلى ملاحظات عملية مثل:
> "You solve algorithms quickly but spend more time debugging memory-related issues."

> **Planned product design — not a delivered capability.**

### 🧠 Developer Learning Operating System

الرؤية النهائية لـROOT 404 هي دمج كل الأنظمة السابقة في دورة حياة واحدة:

```text
                         ROOT 404
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
      LEARN              COMPETE            COMMUNITY
        │                   │                   │
   ┌────┼────┐         ┌────┼────┐        ┌────┼────┐
   │    │    │         │    │    │        │    │    │
Projects AI  Skill    Arena Daily Exam   Rooms Mentor
   │    │   Graph       │    │
   └────┴────┬───────────┴────┘
              │
         CODE ENGINE
              │
     ┌────────┼─────────┐
     │        │         │
 Moulinette Sandbox  AI Review
     │        │         │
     └────────┼─────────┘
              │
         PEER REVIEW
              │
       REPUTATION SYSTEM
              │
         LEVEL / XP
              │
       ┌──────┴──────┐
       │             │
   PORTFOLIO     LEADERBOARD
       │
       ▼
   HIRING PORTAL
```

الهدف النهائي:

**Beginner → Student → Coder → Advanced Developer → Mentor → Professional**

ROOT 404 لا تكون مجرد موقع لتعلم البرمجة، بل **بيئة متكاملة لإدارة رحلة المبرمج وتطوير مهاراته وإثباتها وبناء مجتمعه المهني.**

---

> **Planned product design — not a delivered capability.**

## 🗺️ خارطة الطريق المحدّثة (Ultimate Roadmap)

> **Planned product design — not a delivered capability.**

### Phase 1 — Core MVP
- [ ] Auth + User Profiles
- [ ] Dashboard
- [ ] Projects & Path System
- [ ] Monaco Code Editor
- [ ] Docker/Ubuntu Sandbox
- [ ] Moulinette / Judge Engine
- [ ] AI Mentor الأساسي
- [ ] Peer Review
- [ ] Collaboration Rooms
- [ ] XP / Level System
- [ ] Leaderboard
- [ ] Basic Profile

> **Planned product design — not a delivered capability.**

### Phase 2 — Learning Intelligence
- [ ] Code Journey
- [ ] Skill Graph
- [ ] Knowledge Gap Detection
- [ ] Adaptive Path Engine
- [ ] Smart Peer Matchmaking
- [ ] AI Code Review
- [ ] Daily Missions
- [ ] Streak & Anti-Burnout
- [ ] Learning Velocity
- [ ] Student Analytics 360°

> **Planned product design — not a delivered capability.**

### Phase 3 — Competitive & Social Layer
- [ ] ROOT Arena
- [ ] Advanced Reputation
- [ ] Trust / Integrity Score
- [ ] Coalition Wars
- [ ] Seasonal Events
- [ ] Pair Programming
- [ ] Live Coding
- [ ] Community Roles

> **Planned product design — not a delivered capability.**

### Phase 4 — Professional Layer
- [ ] Developer Portfolio Generator
- [ ] Public Developer Profiles
- [ ] Mentorship System
- [ ] Corporate & Hiring Portal
- [ ] Hiring Challenges
- [ ] Partner Fair
- [ ] Public Developer API
- [ ] Webhooks

> **Planned product design — not a delivered capability.**

### Phase 5 — Advanced Academy
- [ ] CTF Track
- [ ] AI/ML Bootcamp
- [ ] System Design Labs
- [ ] Algorithmic Dojo
- [ ] Open Source Contributions
- [ ] Exam Mode
- [ ] Polyglot Sandbox
- [ ] Interactive Test Mode

> **Planned product design — not a delivered capability.**

### Phase 6 — ROOT 404 Ecosystem
- [ ] Multi-Campus
- [ ] Inter-Campus Tournaments
- [ ] National Leaderboard
- [ ] Cross-Campus Access
- [ ] Advanced Mentorship Network
- [ ] Partner Ecosystem
- [ ] Global Public Beta

> **Planned product design — not a delivered capability.**

### 🎯 مبدأ التنفيذ

رغم أن الرؤية النهائية كبيرة، لا يتم تطوير كل الأنظمة في وقت واحد.

**الأولوية:**

```text
Moulinette
    ↓
Sandbox
    ↓
Projects
    ↓
Peer Review
    ↓
AI Mentor
    ↓
Dashboard
    ↓
Community
    ↓
Intelligence
    ↓
Competition
    ↓
Professional Ecosystem
```

كل Phase يجب أن تكون قابلة للاستخدام والاختبار قبل الانتقال إلى الـPhase التالية.
