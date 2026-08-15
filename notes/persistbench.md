# PersistBench — Detailed Research Notes

## Paper

**Title:** PersistBench: Evaluating the Safety of Persistent Memory in LLMs

**arXiv:** 2602.01146

**Paper:** https://arxiv.org/abs/2602.01146

**Repository:** https://github.com/ivaxi0s/PersistBench

**Research area:**
- Large Language Models
- Long-term conversational memory
- AI safety
- LLM evaluation
- Sycophancy
- Contextual integrity
- Memory safety

---

# 1. Motivation

Modern conversational assistants increasingly use persistent memory.

Instead of treating every conversation as independent, an assistant can
retain information about a user across conversations.

Example:

Conversation 1:

User:
"I am vegetarian."

The system stores:

Memory:
"User is vegetarian."

Conversation 2:

User:
"Can you recommend something for dinner?"

The assistant can use the previous memory to personalize the response.

This creates a useful capability:

    Persistent memory
          ↓
    Personalization
          ↓
    Better responses

However, persistent memory also introduces a new class of risks.

A memory that is useful in one context may be inappropriate in another.

The central concern of PersistBench is therefore not simply:

    "Can the model remember?"

but:

    "Can the model use persistent memory appropriately?"

---

# 2. Research Gap

Previous conversational-memory benchmarks primarily evaluate whether
models can retrieve or recall information from previous interactions.

Examples include:

- LoCoMo
- LongMemEval
- MemoryBank

These works largely focus on:

    Memory → Retrieval → Answer

PersistBench focuses on:

    Memory → Should this memory influence the answer?
                    ↓
              Appropriate / Inappropriate

Therefore, the paper shifts the problem from:

    Memory recall

to:

    Memory use and misuse

---

# 3. Core Research Question

The paper investigates whether persistent memories can cause
LLMs to behave incorrectly even when the memory is available to
the model in a technically correct form.

Two primary safety failure modes are studied:

1. Cross-domain memory leakage
2. Memory-induced sycophancy

A third category is included to ensure that models are still capable
of using memory appropriately:

3. Beneficial memory use

---

# 4. Persistent Memory Formulation

The paper represents a user's long-term memory as:

    M_u = {m_1, m_2, ..., m_n}

where:

    M_u = user's memory
    m_i = an individual textual memory

Example:

    M_u = {
        "User is vegetarian.",
        "User works in finance.",
        "User likes cricket.",
        "User believes X."
    }

A new user query is represented as:

    q

The model receives memory and query together.

Conceptually:

    [M_u || q]

where || represents concatenation.

The LLM then produces:

    y ~ f_theta(. | [M_u || q])

where:

    y       = generated response
    f_theta = language model
    M_u     = persistent memory
    q       = current query

Important observation:

PersistBench treats memory primarily as textual information available
to the model.

It does not require a specific memory extraction architecture.

---

# 5. Failure Mode 1 — Cross-Domain Memory Leakage

## Definition

Cross-domain leakage occurs when information from one domain
inappropriately influences a response in another domain.

For example:

Memory:

    "User has a medical condition."

Memory domain:

    Health

Current query:

    "Help me write an email to my professor."

Query domain:

    Education / Work

The health memory should not influence the response.

A failure occurs if the model incorporates information from the
unrelated memory into its response.

Important distinction:

The mere presence of an unrelated memory is NOT automatically a failure.

The memory must actually influence the response inappropriately.

Conceptually:

    d(m) != d(q)
           +
    memory influences response
           ↓
    Cross-domain leakage

---

# 6. Failure Mode 2 — Memory-Induced Sycophancy

Sycophancy is an existing problem in LLMs where models tend to
agree with users rather than accurately represent evidence.

PersistBench studies a specific form:

    User belief
        ↓
    Persistent memory
        ↓
    Future query
        ↓
    Model response becomes biased toward user's belief

Example:

Conversation 1:

    User:
    "I strongly believe X."

Stored memory:

    "User believes X."

Later:

    User asks an objective question related to X.

The correct answer should be independent of the user's belief.

If the stored belief causes the model to shift its answer toward
the user's position, this is memory-induced sycophancy.

Important distinction:

Agreement itself is not necessarily a failure.

The failure is:

    Stored user belief
          ↓
    Unwarranted influence
          ↓
    Less truth-oriented response

---

# 7. Beneficial Memory

PersistBench includes beneficial-memory examples to prevent a
trivial strategy:

    "Never use memory."

A model that completely ignores memory could achieve:

    Very low leakage
    Very low sycophancy

while being useless as a personalized assistant.

Therefore, a good memory system should:

    Use relevant memory
          AND
    Suppress irrelevant memory

Example:

Memory:

    "User is allergic to peanuts."

Query:

    "Recommend a snack."

Correct behavior:

    Use the memory.

Therefore:

    Safe memory system != memory-free system

Instead:

    Safe memory system =
        appropriate memory utilization
        +
        appropriate memory restraint

---

# 8. Important Conceptual Distinction

A key observation from reading PersistBench:

    Memory utilization
            !=
    Memory restraint

A model can be good at using relevant memories without being
good at suppressing irrelevant memories.

Conversely, a model can avoid memory misuse simply by
ignoring most memories.

Therefore memory capability should not be considered
one-dimensional.

Potential dimensions:

## 8.1 Memory Utility

Did the system use memory when it should?

## 8.2 Memory Restraint

Did the system avoid memory when it should not be used?

## 8.3 Memory Integrity

When memory was used, was the correct/current interpretation used?

Potential conceptual model:

                 MEMORY CAPABILITY
                        |
          +-------------+-------------+
          |             |             |
        Utility      Restraint     Integrity
          |             |             |
       "Use it"      "Don't use"   "Use it correctly"

This distinction may be important for our future research.

---

# 9. Benchmark Generation

PersistBench contains:

    500 total samples

    200 cross-domain leakage
    200 memory-induced sycophancy
    100 beneficial memory

The benchmark is not generated purely randomly.

The authors use:

    Monte Carlo Tree Search (MCTS)

to search for difficult memory-query combinations.

---

# 10. Why MCTS?

Random generation may produce many easy examples.

Example:

    Memory:
    "User likes coffee."

    Query:
    "What is TCP?"

This is obviously unrelated and may not expose subtle model behavior.

Instead, PersistBench searches for examples that are more likely
to trigger the target failure.

Conceptually:

    Seed
      ↓
    Generate memory + query
      ↓
    Evaluate model behavior
      ↓
    Score candidate
      ↓
    Explore promising candidates
      ↓
    Generate variations
      ↓
    Repeat

The search therefore concentrates on difficult cases.

---

# 11. MCTS Search Process

Each MCTS node represents a candidate:

    (M_u, q)

The generator model creates variations of a candidate.

Possible modifications include:

- Memory content
- Belief strength
- Query wording
- Query domain

Example:

Parent:

    User strongly believes X.

Children:

    User mildly believes X.

    User strongly believes X.

    User is extremely confident X is true.

    Same belief + different query.

The search explores which variants produce stronger failures.

---

# 12. Reward / Judge

Candidate responses are evaluated by a separate judge model.

The general pipeline is:

    Candidate
        ↓
    Target LLM
        ↓
    Response
        ↓
    Judge LLM
        ↓
    Failure score
        ↓
    MCTS reward

The judge provides a Likert-style score.

Higher score indicates stronger evidence of the target
failure behavior.

---

# 13. Exploration vs Exploitation

MCTS uses UCT (Upper Confidence Bound for Trees).

The basic problem is:

    Explore new possibilities

versus:

    Continue exploring configurations that already
    appear to produce failures.

Conceptually:

    UCT =
        observed reward
        +
        exploration bonus

This prevents the search from only exploiting the first
successful failure pattern.

---

# 14. Held-Out Model Validation

The benchmark generation process uses target models to search
for difficult examples.

However, the authors also evaluate candidate examples on
held-out models.

Purpose:

    Prevent benchmark overfitting to the models used
    during generation.

Pipeline:

    Generation / Search models
             ↓
        Candidate samples
             ↓
        Held-out models
             ↓
        Generalization test

If a sample only breaks the original search models, it may
not represent a general weakness.

If it also breaks held-out models, the evidence is stronger.

---

# 15. Memory Expansion

During MCTS, the authors initially work with relatively small
memory sets.

After finding useful failure-inducing memories, additional
irrelevant memories are added.

Conceptually:

    Core memories
        ↓
    Failure-inducing scenario
        ↓
    Add distractor memories
        ↓
    More realistic memory bank

Final benchmark samples contain multiple memories.

This attempts to approximate the clutter of real long-term
memory.

---

# 16. Human Validation

Generated samples are manually checked.

Humans evaluate things such as:

1. Is the memory plausible?

2. Is the query natural?

3. Does the sample actually test the intended failure?

4. Is the domain distinction valid?

5. Is the beneficial-memory label reasonable?

This reduces the risk of nonsensical LLM-generated benchmark cases.

---

# 17. Benchmark Categories

## Cross-domain

200 samples.

The memory and query come from different domains.

Potential domains include:

- Health
- Work
- Finance
- Legal
- Relationships
- Beliefs
- Social
- Identity
- Private thoughts
- Education

The central question:

    Does information from one domain
    improperly influence another?

---

## Sycophancy

200 samples.

The memory contains information about the user's beliefs,
attributes, or positions.

The query is designed so that the correct answer should not
depend on the user's belief.

The central question:

    Does persistent knowledge of the user's belief
    make the model more agreeable to that belief?

---

## Beneficial Memory

100 samples.

The query genuinely benefits from one or more memories.

Examples include:

- Direct fact retrieval
- Multiple-memory retrieval
- Multi-hop reasoning
- Distractor memories

The central question:

    Can the model actually use memory when it is useful?

---

# 18. Evaluation

PersistBench primarily uses an LLM-as-a-judge approach.

For each sample:

    Memory + Query
          ↓
        Model
          ↓
       Response
          ↓
     Judge Model
          ↓
       Score

For leakage and sycophancy, the judge assigns a score
on a 1–5 scale.

Higher score:

    stronger evidence of failure

The paper treats scores at or above the defined threshold
as failures.

Important methodological concern:

    The benchmark's numerical failure rates depend on
    the judge's interpretation.

Therefore:

    LLM-as-judge ≠ perfect ground truth

Human validation and other robustness checks are important.

---

# 19. Major Results

PersistBench reports very high failure rates for targeted
memory misuse.

Approximate median failure rates across evaluated models:

    Cross-domain leakage:
    ~53%

    Memory-induced sycophancy:
    ~97%

Important interpretation:

These are NOT estimates of how often normal ChatGPT conversations
experience memory leakage.

The benchmark deliberately searches for difficult examples.

Therefore the correct interpretation is:

    Current LLMs are highly vulnerable to targeted
    persistent-memory misuse.

Not:

    "53% of all conversations leak memory."

---

# 20. Key Result — Utility vs Safety

One of the most important findings is that beneficial-memory
performance is only weakly correlated with the safety metrics.

This supports the distinction:

    Good at using memory
            !=
    Good at using memory safely

This is particularly relevant to our research direction.

A system could:

    High utility
    High misuse

or:

    Low utility
    Low misuse

The ideal system should achieve:

    High utility
    +
    High restraint
    +
    High integrity

---

# 21. Important Limitation — Static Memory

A major limitation relevant to our future work:

PersistBench primarily evaluates a memory set together with
a query.

Conceptually:

    Memory snapshot + Query → Response

Real users have longitudinal histories:

    Day 1
       ↓
    Conversation
       ↓
    Memory
       ↓
    Day 30
       ↓
    New information
       ↓
    Memory update
       ↓
    Day 90
       ↓
    Contradiction
       ↓
    Memory update

Real memory is dynamic.

This motivates studying:

    Memory evolution
    Temporal validity
    Contradiction
    Updating
    Correction
    Forgetting

---

# 22. Important Limitation — Memory Representation

PersistBench largely treats memories as textual statements.

Example:

    "User prefers Python."

But a real memory could contain:

    content
    source
    timestamp
    confidence
    evidence
    domain
    temporal scope
    sensitivity
    confirmation history
    contradictions

Potential future representation:

    Memory =
        {
            content,
            type,
            timestamp,
            provenance,
            confidence,
            stability,
            status
        }

---

# 23. Important Limitation — Memory Lifecycle

Memory is not simply:

    KEEP
    or
    FORGET

Potential memory actions include:

    KEEP
    UPDATE
    MERGE
    ARCHIVE
    DOWNWEIGHT
    SUPPRESS
    ASK USER
    FORGET

A future memory architecture could model these as explicit
state transitions.

Potential state machine:

    NEW
      ↓
    ACTIVE
      ↓
    +-----------+
    |           |
  STALE      CONFLICTED
    |           |
    ↓           ↓
  ARCHIVED    UPDATED
    |
    ↓
  FORGOTTEN

This is a potential direction for our project.

---

# 24. Important Limitation — Temporal Change

A memory can be true at one point and false later.

Example:

    Day 1:
    "I use Python."

    Day 60:
    "I've switched to Rust."

A static memory bank may contain both statements.

A robust system should understand:

    Historical:
    Python

    Current:
    Rust

This creates a temporal reasoning problem.

Potential research question:

    Can an LLM distinguish what was true
    from what is currently true?

---

# 25. Important Limitation — Provenance

Not all memories have equally strong evidence.

Compare:

    "User casually mentioned Python once."

versus:

    "User explicitly stated they switched
     their entire workflow to Rust."

versus:

    "User repeatedly confirmed they use Rust."

A memory system should potentially consider:

    Source
    Recency
    Repetition
    Explicitness
    Confidence

Potential research question:

    Does explicit provenance improve memory selection
    and reduce inappropriate memory influence?

---

# 26. Important Limitation — Memory Types

Different information may require different memory policies.

Possible types:

    Preference
    Fact
    Temporary state
    Belief
    Intention
    Sensitive information
    Historical information

Example:

    "I like Python."
        → potentially long-term

    "I have an exam tomorrow."
        → temporary

    "I believe X."
        → epistemic belief

    "I am currently visiting Delhi."
        → time-dependent

A single retention policy may be inappropriate for all types.

---

# 27. Important Limitation — Memory Poisoning

Persistent memory could become an attack surface.

Potential attack:

    Attacker
       ↓
    Malicious conversation
       ↓
    Memory extraction
       ↓
    Malicious persistent memory
       ↓
    Future conversations
       ↓
    Model behavior influenced

Research question:

    Can persistent memory be poisoned?

Potential defenses:

    Provenance
    Confidence
    Source validation
    Contradiction detection
    User confirmation
    Memory isolation

---

# 28. Important Limitation — Downstream Actions

PersistBench primarily evaluates:

    Memory → Response

Agentic systems may perform:

    Memory
       ↓
    Reasoning
       ↓
    Tool
       ↓
    Action

A memory could therefore influence an external action.

Example:

    "User usually approves expenses under X."

A dangerous agent might interpret this as authorization.

Future research could investigate:

    Memory → Reasoning → Action

rather than only:

    Memory → Text response

---

# 29. Our Initial Research Direction

Working project name:

    Contextual Memory Management

Possible research framing:

    Can contextual, temporal, and provenance-aware memory
    improve the trade-off between memory utility and
    memory restraint in longitudinal LLM agents?

Potential dimensions:

    1. Temporal evolution
    2. Memory provenance
    3. Memory lifecycle
    4. Utility vs restraint
    5. Memory integrity
    6. Contradiction / correction

---

# 30. Proposed Memory Object

Initial concept:

    Memory(
        content,
        type,
        timestamp,
        confidence,
        provenance,
        status
    )

Example:

    content:
    "User prefers Python"

    type:
    preference

    timestamp:
    2026-08-10

    confidence:
    0.91

    provenance:
    conversation_17

    status:
    active

---

# 31. Proposed Memory State

Potential states:

    NEW
    ACTIVE
    STALE
    CONFLICTED
    ARCHIVED
    FORGOTTEN

Example:

    Day 1:
    "I use Python."
        ↓
    ACTIVE

    Day 60:
    "I've switched to Rust."
        ↓
    CONFLICTED

    Day 61:
    Rust becomes current
    Python becomes historical

This allows the system to distinguish:

    Current information
    Historical information
    Contradicted information

---

# 32. Proposed Evaluation Dimensions

Instead of treating memory performance as one number:

## Memory Utility

    Did the system use memory when it should?

## Memory Restraint

    Did the system avoid memory when it should not be used?

## Memory Integrity

    Did the system use the correct/current interpretation?

## Memory Update Accuracy

    Did the system correctly update memories
    when new evidence appeared?

## Provenance Sensitivity

    Does evidence quality influence memory confidence?

---

# 33. Potential Experiments

### Experiment 1 — PersistBench reproduction

Compare our baselines against PersistBench.

Purpose:

    Establish compatibility with existing research.

---

### Experiment 2 — Temporal evolution

Create multi-day synthetic conversations.

Test:

    Stable facts
    Temporary information
    Changed preferences
    Contradictions

---

### Experiment 3 — Provenance

Compare:

    No provenance
    Basic provenance
    Provenance + confidence
    Provenance + contradiction history

---

### Experiment 4 — Utility vs restraint

Measure separately:

    Utility score
    Restraint score
    Integrity score

Test whether:

    correlation(utility, restraint)

is high or low.

---

### Experiment 5 — Memory poisoning

Introduce false or malicious memories.

Measure:

    Detection
    Retention
    Retrieval
    Correction

---

# 34. Research Questions

Potential RQ1:

    Are memory utilization and memory restraint
    independent capabilities?

Potential RQ2:

    Does temporal state improve the handling of
    changing user information?

Potential RQ3:

    Does provenance improve memory reliability?

Potential RQ4:

    Can explicit memory lifecycle states reduce
    inappropriate memory influence?

Potential RQ5:

    Can memory systems detect and correct
    persistent false information?

---

# 35. Current Hypotheses

H1:

    Memory utility and memory restraint are not
    strongly correlated.

H2:

    Temporal memory states reduce errors caused
    by outdated information.

H3:

    Provenance-aware memories are less likely to
    produce inappropriate responses.

H4:

    Explicit memory lifecycle management improves
    memory integrity without significantly reducing
    beneficial personalization.

---

# 36. What We Must NOT Claim Yet

We have NOT yet demonstrated:

    - Our architecture works.
    - Provenance improves safety.
    - Temporal memory improves performance.
    - Memory utility and restraint are independent.
    - Our method beats PersistBench baselines.

These are hypotheses.

Results must come from experiments.

---

# 37. Current Research Status

Status:

    [x] Read PersistBench motivation
    [x] Understand benchmark categories
    [x] Understand memory formulation
    [x] Understand MCTS generation
    [x] Understand evaluation framework
    [x] Identify potential limitations
    [ ] Reproduce benchmark
    [ ] Inspect raw benchmark samples
    [ ] Establish baselines
    [ ] Design our memory representation
    [ ] Implement temporal state
    [ ] Implement provenance
    [ ] Design new evaluation set
    [ ] Run experiments
    [ ] Analyze results
    [ ] Write research article

---

# 38. Research Principle

Do not design the architecture around a desired result.

First reproduce the baseline.

Then formulate hypotheses.

Then run controlled experiments.

If our architecture performs worse, investigate why.

Unexpected negative results are still useful research findings.