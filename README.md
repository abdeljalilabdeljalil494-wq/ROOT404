<div align="center">

# 🇹🇳 École 1337
### Elite Coder Platform — TounsiCoder-AI

**منصة تعليمية وتنافسية متكاملة مستوحاة من فلسفة École 42، مصمّمة خصيصًا لطلاب ومبرمجي تونس**

[![Status](https://img.shields.io/badge/status-in%20development-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)]()
[![Frontend](https://img.shields.io/badge/frontend-React-61DAFB)]()
[![Sandbox](https://img.shields.io/badge/sandbox-Docker-2496ED)]()

</div>

---

## 📖 جدول المحتويات

- [الفكرة العامة](#-الفكرة-العامة-ورؤية-النظام)
- [ما الذي يميّز École 1337؟](#-ما-الذي-يميّز-école-1337)
- [نظام التقييم الند-للند (مستوحى من 42)](#-نظام-التقييم-الند-للند-peer-to-peer-evaluation)
- [نظام Black Hole والمسار الزمني](#-نظام-black-hole-والمسار-الزمني)
- [نظام Coalitions](#-نظام-coalitions-التحالفات)
- [أنظمة ROOT 404 Ultimate](#-أنظمة-root-404-ultimate)
- [البنية التحتية](#️-البنية-التحتية-وهندسة-النظام)
- [هيكلة المشروع](#-هيكلة-المشروع)
- [التقنيات المستخدمة](#-التقنيات-المستخدمة-tech-stack)
- [خارطة الطريق](#️-خارطة-الطريق-roadmap)
- [المساهمة](#-المساهمة-contributing)

---

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

## 🚀 ما الذي يميّز École 1337؟

هذا هو الجزء الجديد الذي يقرّب المنصة أكثر من فلسفة 42 الأصلية، مع لمسة عصرية بالذكاء الاصطناعي:

### 🕳️ نظام Black Hole والمسار الزمني

بدل نظام تسجيل تقليدي، كل طالب يدخل بـ **"عداد بقاء" (Survival Timer)**:

- كل مسار (Path) له مدة زمنية معيّنة لإتمامه والوصول لمستوى معيّن (مثلاً 3 أشهر للوصول للـ Level 5).
- إذا تجاوز الطالب المدة بدون تقدّم كافٍ، يدخل في **"منطقة الخطر" (Warning Zone)** يتوصل فيها بتنبيهات والمساعد الذكي يقترح خطة تدارك.
- عدم التقدم يؤدي لتفعيل **Black Hole**: تجميد الحساب مؤقتًا وإعادة توزيع الأولوية للطلبة النشيطين — تمامًا كما في 42 الحقيقية، لكن بمرونة أكبر ونظام إنذار مسبق بالذكاء الاصطناعي بدل المفاجأة الكاملة.

### 👥 نظام Peer-to-Peer Evaluation (تصحيح بين الطلبة)

بالتوازي مع الـ Moulinette الآلية، نضيف طبقة تصحيح بشرية حقيقية:

- بعد اجتياز مشروع الـ Moulinette آليًا، يُطلب من الطالب **حجز جلسة تصحيح (Correction Slot)** مع طالب آخر وصل لنفس المستوى أو أعلى.
- كل جلسة توثّق عبر **Video/Chat Room مدمج** داخل المنصة (WebRTC) مع Checklist تفاعلي يظهره النظام تلقائيًا حسب المشروع.
- الطالب المُصحِّح يكسب **نقاط تصحيح (Correction Points)** إضافية إلى جانب رصيده العادي، ما يشجع الطلبة المتقدمين على البقاء نشيطين ومساعدة غيرهم.
- نظام تقييم ثنائي الاتجاه: الطالب يقيّم جودة التصحيح، والمصحِّح يقيّم جدية الطالب — يغذّي هذا **"مؤشر السمعة" (Reputation Score)** الظاهر على البروفايل.

### 🏘️ نظام Coalitions (التحالفات)

كما في 42، الطلبة يُقسّمون تلقائيًا (أو باختيارهم) إلى **تحالفات/بيوت (Coalitions)** بألوان وهويات مختلفة:

- كل تحالف يجمع نقاط من إنجازات أعضائه (مشاريع منجزة، تصحيحات، مساهمات في تحديات جماعية).
- **لوحة ترتيب تحالفات** منفصلة عن الترتيب الفردي، تُحدّث أسبوعيًا.
- فعاليات دورية (Coalition Wars): تحديات برمجية جماعية بمهلة 48 ساعة، تحاكي "Hackathons" داخلية.

### 🤖 المساعد الذكي كموجّه وليس كحلّال

لضمان روح "التعلّم الذاتي" الأصيلة في 42، المساعد الذكي **AI Assistant** مُقيَّد بقواعد صارمة:

- لا يعطي الحل النهائي مباشرة، بل يطرح أسئلة موجِّهة (Socratic Hints) ويشرح المفاهيم فقط.
- يحلّل الأخطاء الشائعة في كود الطالب ويقترح موارد تعليمية (لا حلول جاهزة).
- عند اكتشاف نمط "نسخ-لصق" مشبوه، يُبلّغ نظام Anti-Cheating تلقائيًا.

### 🏆 نظام المستويات المرن (Level System)

مقياس مستويات مستمر من **0.00 إلى 21.00** (بالضبط كما في 42)، حيث:
- كل مشروع يضيف نسبة مئوية من مستوى معيّن حسب الصعوبة ونقاط التصحيح.
- شارات إنجاز مرئية (Badges) تُعرض على البروفايل العام والـ Leaderboard.

---

## 🧠 أساليب ومحتويات متقدمة (Advanced Systems)

### 🏊 نظام Piscine (المعسكر التمهيدي المكثّف)

قبل الدخول للمسار الرئيسي، كل طالب جديد يمرّ بـ **Piscine** — معسكر تمهيدي مكثّف يحاكي فلسفة القبول في 42:

- مدة 4 أسابيع، تمارين يومية تتصاعد صعوبتها تدريجيًا (من أساسيات المنطق البرمجي إلى مشروع جماعي ختامي).
- تقييم يومي آلي + تصحيح ند-للند إجباري لكل تمرين.
- **مؤشر ثبات الأداء (Consistency Score)**: لا يكفي حل التمارين، بل الحفاظ على انتظام يومي — ينعكس على معايير القبول النهائي.
- في نهاية الـ Piscine، يُحسب **معدّل قبول** مبني على: نسبة الإنجاز، جودة الكود (Norme)، ونشاط التصحيح.

### 🎯 محرك توصية المسار (Adaptive Path Engine)

بدل مسار ثابت للجميع، نظام توصية ذكي يبني مسارًا شخصيًا لكل طالب:

- يحلل نقاط القوة/الضعف من نتائج الـ Piscine ومشاريع البداية (خوارزميات، بنى معطيات، أنظمة، ويب...).
- يقترح ترتيب مشاريع مخصص، ويعيد التوصية ديناميكيًا كل ما أنهى الطالب مشروعًا جديدًا.
- يكتشف "الفجوات المعرفية" (Knowledge Gaps) ويقترح تمارين تقوية قصيرة قبل مشروع صعب.

### 🧩 مكتبة تحديات متقدمة (Advanced Challenge Library)

طبقة محتوى إضافية فوق المسارات الأساسية:

| الفئة | أمثلة محتوى |
|---|---|
| **Algorithmic Dojo** | تحديات خوارزميات تنافسية بنمط Competitive Programming (شبيهة بـ Codeforces) مع مؤقت وترتيب مباشر |
| **System Design Labs** | تمارين تصميم أنظمة (Load Balancing, Caching, Microservices) بمخططات تفاعلية |
| **Security CTF Track** | تحديات أمن معلوماتي (Capture The Flag) بمستويات Web, Crypto, Reverse Engineering |
| **AI/ML Bootcamp Track** | مسار متقدم في تعلّم الآلة يُبنى فوق أساسيات Python، بمشاريع تدريجية (من Regression إلى Mini-LLM) |
| **Open Source Contributions** | مهام حقيقية من مشاريع مفتوحة المصدر مرتبطة عبر GitHub API، تُقيَّم كمشاريع معتمدة |

### 📊 لوحة تحليلات متقدمة (Advanced Analytics Dashboard)

لوحة بيانات شخصية لكل طالب مبنية على تحليل سلوكي حقيقي:

- **خريطة حرارية للنشاط** (Activity Heatmap) شبيهة بـ GitHub Contributions.
- **تحليل زمن الحل** (Time-to-Solve Trends) لكل نوع مشروع، لمقارنة تطور الطالب عبر الزمن.
- **توقع الإنجاز** (Completion Forecast): تقدير ذكي لتاريخ إنهاء المسار الحالي بناءً على وتيرة التقدم.
- تقرير أسبوعي آلي يُرسل بالبريد يلخّص التقدم، نقاط التصحيح، وترتيب التحالف.

### 🛡️ طبقة أمان وموثوقية متقدمة

- **Sandbox Hardening**: عزل كل حاوية Docker بحدود صارمة على CPU/RAM/Network (لا اتصال إنترنت خارجي أثناء التنفيذ) لمنع أي استغلال.
- **Code Fingerprinting**: مقارنة تشابه الكود بين تسليمات الطلبة (Plagiarism Detection) عبر تحليل AST وليس نصًا خامًا، لتفادي الإيجابيات الخاطئة.
- **Audit Trail كامل**: تسجيل كل عملية حسّاسة (تسليم، تصحيح، تعديل نقاط) في سجل غير قابل للتعديل، لضمان الشفافية عند النزاعات.
- **Rate Limiting & Abuse Detection** على مستوى الـ API لمنع إغراق نظام الـ Moulinette بطلبات وهمية.

### 🔌 API عام للمطوّرين (Public Developer API)

لفتح المنصة على أدوات وتكاملات خارجية:

- **REST + Webhooks** تتيح لأي طالب ربط إنجازاته بأدوات خارجية (بورتفوليو شخصي، بوت Discord/Telegram للتنبيهات).
- **Public Profile API**: عرض مستوى الطالب، الشارات، وسجل المشاريع كـ Widget قابل للتضمين في مواقع خارجية (شبيه بشارة 42).
- توثيق تفاعلي عبر **Swagger/OpenAPI** مدمج مباشرة من FastAPI.

### 🎮 تعزيز التحفيز (Gamification Layer 2.0)

- **نظام شارات متعدد الطبقات** (Bronze/Silver/Gold/Legendary) لكل فئة إنجاز (سرعة، جودة كود، مساعدة الغير).
- **تحديات موسمية** (Seasonal Events): فعاليات محدودة زمنيًا بمكافآت رموز إضافية.
- **نظام إحالة (Referral System)**: مكافأة الطلبة الذين يجلبون زملاء جدد ينجحون في اجتياز الـ Piscine.

---

### 🧬 نظام Exam Mode (الامتحانات المعزولة)

طبقة تقييم رسمية منفصلة عن المشاريع اليومية، تُستخدم لقياس المستوى الحقيقي:

- **بيئة امتحان مقفلة (Locked-Down Browser/Sandbox)**: تعطيل النسخ/اللصق الخارجي، منع فتح تبويبات أخرى، ومراقبة الكاميرا اختياريًا بموافقة الطالب.
- **تصحيح ند-للند إجباري فور انتهاء الوقت** — لا يمكن مغادرة القاعة الافتراضية قبل تصحيح زميل آخر.
- **بنك أسئلة عشوائي (Randomized Exercise Pool)**: كل طالب يحصل على تركيبة مختلفة من التمارين بنفس مستوى الصعوبة، لمنع الغش الجماعي.
- نتائج الامتحان تُدرج كـ "بوابة" (Gate) إجبارية للانتقال بين مستويات معينة (Circle/Tier).

### 🌐 نظام Campus متعدد الفروع (Multi-Campus Architecture)

تحضيرًا لتوسّع المنصة على مستوى تونس (تونس العاصمة، صفاقس، سوسة...):

- كل "Campus" افتراضي له لوحة ترتيب، تحالفات، وفعاليات خاصة به.
- **Inter-Campus Tournaments**: مسابقات دورية بين الفروع، بنتائج مجمّعة على لوحة وطنية.
- إمكانية "زيارة افتراضية" (Cross-Campus Access) لطالب من فرع لمشاريع/فعاليات فرع آخر.

### 🧑‍🏫 نظام Mentorship المتقدم

طبقة توجيه فوق نظام التصحيح العادي:

- طلبة بمستوى Level ≥ 15 يمكنهم التسجيل كـ **Mentors** رسميين.
- جلسات توجيه مجدولة (Office Hours) عبر تقويم مدمج، منفصلة عن جلسات التصحيح الإلزامية.
- نظام "مسار الإرشاد" (Mentorship Track): تتبّع تقدّم الطلبة الموجَّهين وربطه بمكافآت للمرشد.

### 🏢 بوابة الشركاء والتوظيف (Corporate & Hiring Portal)

جسر بين المنصة وسوق الشغل التونسي:

- **بروفايل توظيف تلقائي**: يُبنى من سجل المشاريع، الشارات، ومستوى الطالب — قابل للمشاركة كرابط عام.
- شركات شريكة يمكنها نشر **تحديات توظيف (Hiring Challenges)** مخصصة، ومتابعة نتائج المتقدمين مباشرة من لوحة تحكم خاصة.
- **معرض الشركاء (Partner Fair)** افتراضي دوري يجمع الطلبة المتقدمين بأصحاب العمل.

### 🔄 محرك Sandbox متعدد اللغات (Polyglot Execution Engine)

توسعة تقنية لدعم تنويع أعمق في التقييم الآلي:

- كل لغة مدعومة لها **Runner Image** مستقل داخل `judge_sandbox/` (مثال: `runner_c.py`, `runner_python.py`, `runner_js.py`)، لضمان عزل التبعيات.
- **Test Case DSL** موحّد (YAML/JSON) يكتب به المُشرفون حالات الاختبار مرة واحدة، ويُترجم تلقائيًا لصيغة كل لغة.
- دعم **Interactive Test Mode**: بعض المشاريع (مثل بناء Shell أو Server) تحتاج تفاعل حي مع stdin/stdout أثناء الفحص، وليس فقط مقارنة مخرجات نهائية.

### 📚 محتوى تعليمي تكميلي (Knowledge Base & Micro-Learning)

- **Wiki تفاعلي** مبني من مساهمات الطلبة أنفسهم (Peer-Written Docs)، يُراجعه فريق إشراف قبل النشر.
- **Micro-Lessons**: فيديوهات قصيرة (3-5 دقائق) مرتبطة مباشرة بكل مشروع، تُقترح تلقائيًا عند تعثّر الطالب أكثر من مرة معينة.
- **Glossary تفاعلي**: قاموس مصطلحات تقنية بالعربية والفرنسية والإنجليزية، مربوط بالكود مباشرة (Hover-to-Define في المحرر).

---


## 🚀 أنظمة ROOT 404 Ultimate

هذه الطبقة توسّع المنصة من Coding Academy إلى **Developer Learning Operating System**:
بيئة واحدة ترافق المبرمج من مرحلة المبتدئ إلى Developer متقدم، ثم Mentor وProfessional.

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

## 🚀 Démarrage rapide

**Backend** (FastAPI — voir `backend/README.md` pour le détail) :

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # DEBUG=true → le code OTP est renvoyé dans la réponse
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Base de données SQLite créée + seedée automatiquement au premier lancement
(compte de démo : `abdeljalil@root404.tn`). PostgreSQL en production via
`DATABASE_URL`.

**Frontend** (React/Vite) :

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173 — le proxy /api → :8000 est déjà configuré
```

Les services `auth`, `projects` et `dashboard` consomment l'API réelle ; les
autres services restent sur leurs données mock jusqu'à la construction de
leurs endpoints (repli automatique sur le mock si le backend est hors ligne).

---

## 🗺️ خارطة الطريق المحدّثة (Ultimate Roadmap)

### Phase 1 — Core MVP
- [x] Auth + User Profiles — backend OTP/JWT live, login/register branchés
- [x] Dashboard — stats, activité & hebdo calculés en direct
- [x] Projects & Path System — statuts par utilisateur + soumissions en file
- [x] Monaco Code Editor
- [ ] Docker/Ubuntu Sandbox
- [ ] Moulinette / Judge Engine
- [ ] AI Mentor الأساسي
- [ ] Peer Review
- [ ] Collaboration Rooms
- [ ] XP / Level System
- [ ] Leaderboard
- [ ] Basic Profile

> **Statut (06/09/2026)** : le backend FastAPI est en ligne pour le cœur du
> MVP (Auth, Projects, Dashboard) et le frontend est branché dessus. Les UI
> des autres systèmes Phase 1 existent déjà (mock) et seront branchées aux
> endpoints backend dans les étapes suivantes — la prochaine étape est le
> **Judge / Moulinette** (exécution sandboxée + tests), les soumissions étant
> déjà persistées en `pending`.

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

### Phase 3 — Competitive & Social Layer
- [ ] ROOT Arena
- [ ] Advanced Reputation
- [ ] Trust / Integrity Score
- [ ] Coalition Wars
- [ ] Seasonal Events
- [ ] Pair Programming
- [ ] Live Coding
- [ ] Community Roles

### Phase 4 — Professional Layer
- [ ] Developer Portfolio Generator
- [ ] Public Developer Profiles
- [ ] Mentorship System
- [ ] Corporate & Hiring Portal
- [ ] Hiring Challenges
- [ ] Partner Fair
- [ ] Public Developer API
- [ ] Webhooks

### Phase 5 — Advanced Academy
- [ ] CTF Track
- [ ] AI/ML Bootcamp
- [ ] System Design Labs
- [ ] Algorithmic Dojo
- [ ] Open Source Contributions
- [ ] Exam Mode
- [ ] Polyglot Sandbox
- [ ] Interactive Test Mode

### Phase 6 — ROOT 404 Ecosystem
- [ ] Multi-Campus
- [ ] Inter-Campus Tournaments
- [ ] National Leaderboard
- [ ] Cross-Campus Access
- [ ] Advanced Mentorship Network
- [ ] Partner Ecosystem
- [ ] Global Public Beta

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

## 🏗️ البنية التحتية وهندسة النظام (System Architecture)

```text
                        ┌─────────────────────────────────────────┐
                        │   Front-End: Object-Oriented Web Page   │
                        │   Modern UI + Monaco Code Editor        │
                        └────────────────────┬────────────────────┘
                                             │ (REST API / WebSockets)
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │    Back-End API Engine (FastAPI)        │
                        │  Auth (OTP), Tokens, Anti-Cheating Bot  │
                        │  Peer-Evaluation Engine, Black Hole Job │
                        └──────┬──────────────┬──────────────┬────┘
                               │              │              │
              ┌────────────────┘              │              └────────────────┐
              ▼                               ▼                               ▼
    ┌───────────────────┐           ┌───────────────────┐           ┌───────────────────┐
    │  PostgreSQL DB    │           │ Docker Containers │           │  AI Assistant API │
    │ (Object-Oriented  │           │ Ubuntu Container  │           │ Socratic Hints     │
    │  Data Architecture│           │ Moulinette Engine │           │ & Code Explainer   │
    └───────────────────┘           └───────────────────┘           └───────────────────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │  WebRTC Correction     │
                    │  Rooms (Peer Review)   │
                    └───────────────────────┘
```

---

## 📂 هيكلة المشروع (Project Structure)

```text
Tounsicoder-ai/
├── backend/
│   ├── app/
│   │   ├── api/                # Endpoints (auth, rooms, judge, ai, corrections)
│   │   ├── core/                # Config, security, DB connections
│   │   ├── models/               # SQLAlchemy ORM Models (Object-Oriented)
│   │   ├── schemas/              # Pydantic Schemas
│   │   ├── services/
│   │   │   ├── judge.py          # Docker execution logic & Moulinette
│   │   │   ├── ai_helper.py      # LLM API Integration & Socratic Prompts
│   │   │   ├── blackhole.py      # Survival timer & warning zone logic
│   │   │   ├── correction.py     # Peer-to-peer evaluation engine
│   │   │   ├── coalition.py      # Coalitions & team scoring logic
│   │   │   └── room_service.py
│   │   └── main.py               # FastAPI Entrypoint
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/           # CodeEditor (Monaco), RoomCard, Navbar, ChatAI
│   │   ├── pages/                 # Dashboard, PathView, RoomView, Leaderboard, Coalitions
│   │   │   ├── JourneyView         # Code Journey
│   │   │   ├── SkillGraphView      # Skill Graph
│   │   │   ├── ArenaView           # ROOT Arena
│   │   │   ├── PortfolioView       # Public Developer Portfolio
│   │   │   └── AnalyticsView       # Analytics 360°
│   │   ├── services/              # API calls (Axios)
│   │   └── styles/
│   ├── package.json
│   └── Dockerfile
├── judge_sandbox/
│   ├── runner.py                  # Code execution wrapper inside container (Ubuntu)
│   └── Dockerfile.runner          # Isolated runner image
├── docker-compose.yml              # Local development setup
└── README.md
```

---

## 🧰 التقنيات المستخدمة (Tech Stack)

| الطبقة | التقنية |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | React + Monaco Editor |
| Database | PostgreSQL |
| Sandbox | Docker + Ubuntu Container |
| Real-time | WebSockets + WebRTC (لجلسات التصحيح) |
| AI Layer | LLM API (Contextual Hints & Code Explainer) |
| Auth | Email OTP + JWT |
| Collaboration | WebRTC + WebSockets |
| AI | LLM API + Socratic Mentor Layer |
| Execution | Docker + Ubuntu + Resource Limits |
| Code Analysis | AST Fingerprinting + Automated Review |
| Analytics | Event Tracking + Learning Metrics |
| Portfolio | Public Profile / Developer API |


---

## 🗺️ خارطة الطريق (Roadmap)

- [ ] بناء هيكل الـ Backend الأساسي (Auth + Judge Engine)
- [ ] تطوير محرر الكود التفاعلي (Monaco Integration)
- [ ] بناء نظام Moulinette الآلي داخل Docker
- [ ] إطلاق نظام Piscine التمهيدي
- [ ] إطلاق نظام Peer-to-Peer Evaluation
- [ ] تفعيل نظام Coalitions ولوحات الترتيب
- [ ] دمج نظام Black Hole والتنبيهات الذكية
- [ ] إطلاق المساعد الذكي بنمط Socratic Hints
- [ ] بناء محرك توصية المسار (Adaptive Path Engine)
- [ ] إطلاق مكتبة التحديات المتقدمة (Dojo, CTF, AI/ML Track)
- [ ] تفعيل لوحة التحليلات المتقدمة
- [ ] فتح الـ API العام للمطوّرين
- [ ] إطلاق Exam Mode والبيئة المعزولة
- [ ] بناء محرك Sandbox متعدد اللغات
- [ ] تفعيل نظام Mentorship
- [ ] إطلاق بوابة الشركاء والتوظيف
- [ ] دعم بنية Multi-Campus
- [ ] نسخة تجريبية عامة (Public Beta)

---

## 🤝 المساهمة (Contributing)

المساهمات مرحّب بها! إذا كنت تريد المساعدة في تطوير المنصة:

1. اعمل Fork للمشروع
2. أنشئ فرعًا جديدًا (`git checkout -b feature/amazing-feature`)
3. Commit للتغييرات (`git commit -m 'إضافة ميزة رائعة'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. افتح Pull Request

---

<div align="center">

**صُنع بـ ❤️ من أجل مجتمع المبرمجين في تونس**

</div>
