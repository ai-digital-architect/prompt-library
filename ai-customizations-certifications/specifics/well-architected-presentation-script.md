# Well Architected Framework - Presentation Script
## 40-Minute Conversational Presentation for Technical Program/Project Managers

---

### **Slide 1: Title Slide - Well Architected** 
**(1.5 minutes)**

"Good [morning/afternoon] everyone! As program and project managers, we're the ones accountable when systems succeed – and when they fail. Today I want to explore how we build systems we'll be proud of decades from now, not just at the next milestone review.

**[AUDIENCE ENGAGEMENT]** *Quick show of hands – how many of you have inherited a system and thought, 'Why was it built this way?' Now, how many of you worry someone will say the same about yours?*

[Acknowledge responses with a laugh]

That tension between delivery pressure and long-term quality is exactly what we're going to tackle."

---

### **Slide 2: The Safety Pin** 
**(1.5 minutes)**

"The safety pin – unchanged since 1849. Over 170 years, no redesign needed. Why? Because it solves exactly one problem elegantly. No scope creep, no feature bloat. Simple, reliable, done.

As PMs, we love adding requirements. But the best architectures are the ones where someone resisted the urge to over-engineer.

**[AUDIENCE ENGAGEMENT]** *What's the 'safety pin' in your program – the component that just works and nobody touches?*

[Take 1-2 quick responses]

That's the gold standard. Let's figure out how to build more of those."

---

### **Slide 3: The Golden Gate Bridge** 
**(2 minutes)**

"The Golden Gate Bridge – swaying since 1937. Designed to move 27 feet laterally in high winds. It doesn't resist change; it absorbs it.

Here's what I want you to take from this: flexibility isn't a nice-to-have, it's a structural requirement. How many of your programs have had scope changes, team changes, or priority shifts in the last quarter? Probably all of them.

**[AUDIENCE ENGAGEMENT]** *When your last major change request hit, did your system architecture bend or break? What was the cost of that rigidity?*

[Allow 2 quick examples – steer toward cost/schedule impact since PMs relate to that]

The bridge teaches us that adaptability should be in the project plan from day one, not treated as rework."

---

### **Slide 4: Systems Thinking - Iceberg** 
**(2.5 minutes)**

"This iceberg is the most important image in this deck. What we see – events, incidents, outages – is the tip. Below the surface are patterns, structures, and mental models driving everything.

As PMs, we live at the events level. Stakeholder escalation? React. Outage? War room. Missed deadline? Recovery plan. We're professional firefighters.

But the best PMs operate deeper. They ask: Why does this keep happening? What structural decision is causing this pattern? What assumption are we not challenging?

Quick example: A team kept missing sprint commitments. The PM kept adjusting velocity. Below the surface? A shared database dependency that three teams were contending for. One architectural decision – decoupling that dependency – fixed a 'people problem' that was actually a systems problem.

**[AUDIENCE ENGAGEMENT]** *What recurring problem in your program might actually be a systems issue in disguise?*

[Pause – let 1-2 people share]"

---

### **Slide 5: Donella Meadows Quote** 
**(1.5 minutes)**

"Donella Meadows: 'A system is a set of related components that work together in a particular environment to perform whatever functions are required to achieve the system's objective.'

Three words matter here: RELATED. TOGETHER. OBJECTIVE.

As PMs, we manage the 'together' part. We coordinate. But here's the challenge – do your teams actually understand the shared objective? Or is each team optimizing for their own deliverable?

**[QUICK REFLECTION]** *Can you state your system's objective in one sentence – not the project charter, but what it actually does for the end user?*

[5-second pause]

If that was hard, your architecture might be solving the wrong problem."

---

### **Slide 6: Peter Senge Quote** 
**(2 minutes)**

"Peter Senge says systems thinking is about seeing the whole versus parts, patterns versus snapshots, and subtle interconnectedness.

Netflix didn't beat Blockbuster with better technology. They saw patterns of change in consumer behavior. Blockbuster looked at quarterly snapshots and saw a profitable business.

For us as PMs, this is a warning: don't manage by dashboards alone. Green status reports are snapshots. The question is – what patterns are forming beneath those green statuses?

**[AUDIENCE ENGAGEMENT]** *What patterns are you seeing in your programs that aren't yet showing up in your status reports?*

[Take 2 quick observations]

Those hidden patterns are where your real risks live."

---

### **Slides 7-10: Complex Systems (Naval Fleet)** 
**(2 minutes total – advance through slides steadily)**

"This naval fleet perfectly represents what we manage daily. Look at these six properties:

[Slide 8] **Interconnectedness** and **Holistic View** – every ship depends on the others. Sound familiar? Every microservice, every team, every vendor in your program is interconnected. You can't assess risk by looking at one team in isolation.

[Slide 9] **Causality & Patterns** and **Emergence** – the fleet creates capabilities no single ship has. Your system does the same – and sometimes produces behaviors nobody designed.

[Slide 10] **Feedback Loops** and **Dynamic Complexity** – the fleet adapts in real-time. Your system changes with every deployment, every config change, every scaling event.

**[AUDIENCE ENGAGEMENT]** *What's an emergent behavior – good or bad – that surprised you in a system you managed?*

[Take 1-2 examples, then move on]"

---

### **Slide 11: Levels of Thinking** 
**(2.5 minutes)**

"Four levels, and I want you to be brutally honest about where your organization lives:

**EVENTS** → React. Fire drills. Incident response. Most orgs live here.
**PATTERNS** → Anticipate. Trend analysis. Capacity planning. Better, but still reactive.
**STRUCTURES** → Design. Architecture decisions. Team topology. Process design. This is where PMs can have massive impact.
**MENTAL MODELS** → Transform. Challenging assumptions like 'we've always done it this way' or 'the business won't accept downtime for migration.'

Here's the PM insight: every level up you operate, the more leverage you have. Fixing an incident costs hours. Fixing a pattern costs days. Fixing a structure saves months. Changing a mental model changes everything.

**[AUDIENCE ENGAGEMENT]** *What's one mental model – an assumption everyone holds – that's limiting your program right now?*

[Facilitate 2 quick answers]

That's where the real transformation happens."

---

### **Slide 12: Taj Mahal Transition** 
**(30 seconds)**

"The Taj Mahal – stunning since 1632. Nearly 400 years of enduring architecture. Now let's take systems thinking and make it actionable with a concrete framework."

---

### **Slide 13: Well Architected Themes Overview** 
**(3 minutes)**

"Four pillars of well-architected systems:

1. **Durability & Adaptability** – Composable, flexible, maintainable
2. **Scalability** – Modular, standardized, orchestrated
3. **Resiliency** – Prevention, assurance, insurance, adaptability
4. **Operational Excellence** – Manageable, cost-effective, efficient

These map directly to what AWS has formalized in their Well-Architected Framework with six pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, and Sustainability.

For PMs, here's why this matters: AWS provides a free Well-Architected Tool in the console. It gives you a structured review against these pillars. It's essentially a health check for your architecture – and it produces findings you can put directly into your risk register and backlog.

They also have industry-specific lenses – FinTech, Healthcare, Gaming, IoT – and technology-specific ones for Serverless and Machine Learning.

**[AUDIENCE ENGAGEMENT]** *How many of you have used the AWS Well-Architected Review? For those who haven't – what framework do you use to assess architectural health?*

[Take 2 responses]

The key insight is that architecture isn't static. Plan quarterly reviews into your program cadence."

---

### **Slides 14-16: Scalability (Container Ships)** 
**(2.5 minutes total – advance through slides)**

[Slide 14] "Containerization in shipping revolutionized global trade. The same container fits on trucks, trains, and ships. That's standardization enabling scale.

[Slide 15] This port handles thousands of containers daily. They didn't scale by making bigger containers – they improved orchestration. Same principle in software: don't build bigger monoliths, orchestrate smaller standard units.

[Slide 16] The result – thousands of standardized units moving as one system.

For PMs managing growth: the question isn't 'can we handle more load?' It's 'what's our unit of scale, and is it truly standardized?'

**[AUDIENCE ENGAGEMENT]** *What's your unit of scale – microservice, pod, team, feature? And is it genuinely standardized, or does every instance require custom work?*

[Take 1-2 examples]

If scaling requires heroes, you don't have a scalable system."

---

### **Slide 17: Themes Reinforcement** 
**(30 seconds)**

"Quick reinforcement: these four themes are interconnected. You can't scale what isn't durable, protect what isn't resilient, or manage what isn't observable. Now let's go deeper on resiliency."

---

### **Slides 18-19: Resiliency Themes** 
**(2 minutes total)**

"Resiliency breaks into four areas:

**Prevention** – Architecture, design, defensive coding, controls. This is your first line.
**Assurance** – Inspection, quality, observability, audit. Trust but verify.
**Insurance** – Segmentation, redundancy, contingency, repairability. Your safety net.
**Adaptability** – Rollback, failover, elasticity, autonomy. Your recovery muscle.

As PMs, we tend to over-invest in insurance – backups, DR plans, runbooks – because they're tangible deliverables. But prevention is where the highest ROI lives.

**[AUDIENCE ENGAGEMENT]** *Quick gut check: What percentage of your resiliency budget goes to prevention versus recovery? Is that the right ratio?*

[Quick show of hands or 1-2 responses]

Shift left on resiliency the same way you shift left on testing."

---

### **Slides 20-23: Bulkheading Example** 
**(2.5 minutes total – advance through slides)**

[Slide 20-21] "Bulkheading – borrowed from naval architecture. Ships are divided into watertight compartments.

[Slide 22] These blue lines are bulkheads. If one compartment floods, the ship survives because the damage is contained.

[Slide 23] The benefits: integrity, containment, maintainability, repairability.

The Titanic had bulkheads, but they didn't go high enough. Water cascaded over the top. Half-measures in isolation are dangerous – they give you false confidence.

In software: Do your services have true blast radius isolation? If one microservice fails, does it cascade? If a database goes down, how many services follow?

**[AUDIENCE ENGAGEMENT]** *Think about your last major incident – did the failure stay contained, or did it cascade across services? What would a 'bulkhead' have looked like?*

[Take 1-2 examples]

As PMs, we should be asking our architects: 'Show me the blast radius. Show me the bulkheads.'"

---

### **Slide 24: Closing - Charminar** 
**(1 minute)**

"The Charminar – towering since 1591. Over 430 years of endurance.

Our systems won't stand for centuries, but the principles that make them last are the same ones that built these monuments. Before we close, let's talk about why everything we've discussed today becomes even more critical in the age of AI."

---

### **[Additional Section] Systems Thinking in the Age of AI**
**(5 minutes)**

"We're at an inflection point. Generative AI isn't just another feature – it fundamentally changes how systems behave, fail, and scale.

**1. AI Amplifies Complexity**

Traditional systems have predictable failure modes. You deploy code, it does the same thing every time. AI components are non-deterministic – the same input can produce different outputs. For PMs, this means your test plans, acceptance criteria, and quality gates all need rethinking.

The iceberg goes deeper with AI. We're now managing black box models, training data biases that cascade silently, and feedback loops that can spiral without warning.

**[AUDIENCE ENGAGEMENT]** *Who's already managing AI components in their programs? What's been the hardest part from a PM perspective?*

[Take 2 quick examples]

**2. New Architectural Patterns Are Non-Negotiable**

Your architects need to be building:
- **Guardrails, not guidelines** – AI doesn't follow rules, it learns patterns. You need hard boundaries.
- **Continuous validation** – Model drift means your system changes without anyone deploying code. Budget for ongoing monitoring.
- **Ethical bulkheads** – Contain AI decisions that could cause harm. Just like ship bulkheads, isolate the blast radius.

**3. Scale Becomes Existential**

ChatGPT reached 100 million users in 2 months. Instagram took 2.5 years. If your AI-powered feature goes viral, your architecture needs to handle a 100x spike overnight. This isn't theoretical – it's your capacity planning problem right now.

**4. The AWS Framework Evolves**

AWS has added AI-specific lenses: AI Service Reliability, Responsible AI, Cost Explosion Prevention, and Data Governance. As PMs, these give you a structured way to assess AI readiness in your architecture reviews.

Here's the hard truth that matters most for PMs: **AI makes good architecture great and bad architecture catastrophic.** The amplification effect means whatever architectural debt you're carrying will compound faster than ever.

**5. The PM's AI-Era Playbook:**

1. **Design for uncertainty** – Non-deterministic components need wider error margins
2. **Build observability from day one** – You can't manage what you can't see
3. **Plan for 100x scale** – AI adoption curves break historical models
4. **Invest in data governance early** – It's harder and more expensive to add later
5. **Budget for continuous validation** – AI systems need ongoing care, not just deployment

**[FINAL AUDIENCE ENGAGEMENT]** *Looking at your current program roadmap – what's one architectural decision you'd change right now knowing AI will be part of your system within two years?*

[Allow several people to share]

We're the first generation of PMs building systems where components can learn, adapt, and surprise us. The Pantheon builders knew exactly how stone would behave. We don't have that luxury.

But that's also the opportunity. We get to define the governance, establish the patterns, and build the frameworks that will guide system architecture for the next decade.

**Four AI-Era Takeaways:**
1. **Assume AI is coming** – Architect for it now
2. **Build platforms, not point solutions** – AI capabilities evolve rapidly
3. **Governance is a day-one investment** – Not a phase-two add-on
4. **Your architecture IS your competitive advantage** – Modular, observable, scalable

Thank you for this engaging discussion. Remember – as PMs, we don't just deliver projects. We shape the systems that define our organizations for years to come."

---

## **Q&A Session** 
**(Remaining time - approximately 3-5 minutes)**

"I'd love to hear your questions. What resonated? What challenged your thinking? What are you going to do differently on Monday morning?"

"I'd love to hear your questions, challenges, or share more specific examples from your contexts. What resonated with you? What challenged your thinking?"

---

## **Presentation Tips:**

1. **Energy Management**: Start high energy, dip slightly in the middle (systems thinking theory), build back up for practical examples, peak again for AI section

2. **Engagement Frequency**: Ask for participation every 2-3 slides to maintain attention

3. **Story Banking**: Have 2-3 backup stories for each concept in case discussion is limited, especially AI examples

4. **Time Flexibility**: Slides 7-10 and 20-23 can be compressed if running long

5. **Visual Cues**: Point to specific parts of images when discussing (bulkheads, iceberg sections, etc.)

6. **Voice Modulation**: Slow down for quotes, speed up for examples, pause after questions

7. **Response Management**: If someone's answer goes long, politely interrupt with "That's a perfect example, and in the interest of time..."

8. **AI Examples Ready**: Have current AI examples ready (ChatGPT, Copilot, Midjourney) that audience relates to

## **Emergency Time Adjustments:**

- **Running Long**: Skip slide 17, combine slides 7-10 into 2 minutes, shorten AI section to 3 minutes
- **Running Short**: Add more discussion on mental models (slide 11), deeper dive into AWS pillars, or expand AI implications
- **Low Engagement**: Have prepared examples ready to share yourself, especially AI failures/successes

## **Key Phrases for Transitions:**

- "This connects beautifully to..."
- "You might be wondering how this applies to..."
- "Let's make this practical..."
- "Here's where it gets interesting..."
- "Building on what [audience member] just said..."
- "Now, this becomes even more critical with AI because..."
- "The AWS framework addresses this with..."

## **Additional AI Talking Points (if time permits):**

- **GitHub Copilot** changing how we think about code ownership and liability
- **Stable Diffusion** lawsuits highlighting the importance of data governance
- **ChatGPT outages** showing what happens when we don't architect for scale
- **Tesla Autopilot** incidents demonstrating the need for ethical bulkheads
- **Amazon's hiring AI** bias as an example of feedback loops gone wrong
- **Google's Gemini** image generation controversy showing the importance of testing edge cases

## **AWS Well-Architected Specifics to Mention:**

- **Well-Architected Tool** - Free reviews available in AWS Console
- **Lenses** - Industry-specific (FinTech, Gaming, Healthcare) and technology-specific (Serverless, ML, IoT)
- **Pillars interact** - Security affects all other pillars
- **Trade-offs** - Sometimes you optimize one pillar at the expense of another (performance vs. cost)
- **Regular reviews** - Architecture isn't static, review quarterly

## **Final Note:**
The combination of classical architecture examples, systems thinking, AWS framework, and AI implications creates a powerful narrative: We stand on the shoulders of giants (historical architecture), we have frameworks to guide us (AWS Well-Architected), but we face unprecedented challenges (AI) that require us to evolve our thinking. The audience should leave feeling both equipped with practical tools and inspired to tackle the complexity ahead.