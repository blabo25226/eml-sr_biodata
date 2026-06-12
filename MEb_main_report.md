# MEbの読解
*Non-Monotone Response Modules and Cascades from the EML Operator for Reduced
Models of Biological Dynamics
Amir Erez1, ∗
1Racah Institute of Physics, The Hebrew University of Jerusalem, Jerusalem 9190401, Israel
(Dated: May 6, 2026)*
ここでは上記の論文を丁寧に読解していく。

# 1.introduction

<details>
<summary>1.introductionの本文</summary>

Differential equations occupy a central position in
many branches of physics and quantitative biology. They
are useful to identify a small number of state variables,
couplings, and time scales that organize the observed be-
havior [1, 2]. In biological modeling, however, this re-
duction is often quite approximate. Perturbation exper-
iments can reveal overshoot, adaptation, delayed inhibi-
tion, or biphasic dependence, while the underlying bio-
chemical network may be only partially known. In such
cases, one often falls back on standard response functions,
such as Hill-type saturation [3], or on large mechanistic
models whose parameters are difficult to identify. Here,
we explore a controlled way to generate low-dimensional
nonlinear ODEs, that is richer than a fixed phenomeno-
logical curve but more constrained than arbitrary curve
fitting.
Symbolic regression addresses a related problem: given
data, search for an analytic expression that explains it.
Modern approaches have shown that scientific laws and
compact physical relations can sometimes be recovered
from numerical data when the search is constrained by
appropriate inductive biases [4–6]. Dynamical variants,
including sparse identification of nonlinear dynamics,
similarly seek compact governing equations from time-
series data [7–9]. Underlying these methods is a useful
principle: model discovery is more meaningful when the
search grammar, the model-complexity penalty, and the
validation criteria are specified in advance. Otherwise,
a sufficiently expressive symbolic system becomes a lan-
guage for overfitting.
Here, we explore a new grammar for reduced nonlinear
dynamics based on the recently proposed EML operator
∗ amir.erez1@mail.huji.ac.il
by Odrzywolek [10], where the single binary operator
eml(x, y) = exp(x) − ln(y) , (1)
together with the constant 1 can generate the stan-
dard repertoire of elementary functions. In Odrzywolek’s
work, the main point is syntactic universality: elemen-
tary formulae can be represented as binary trees with
internal nodes from the EML operator. Thus, a natural
grammar for symbolic regression emerges. Rather than
searching over many disjoint primitives, e.g., power, ex-
ponential, logarithm, and arithmetic operations, one can
search over EML-generated expression trees, easily trans-
latable into ordinary mathematical form.
We stress that EML is not a new physical or biological
interaction law. A universal expression grammar supplies
syntax, not semantics. Physical or biological interpreta-
tion enters only after the grammar has been restricted
and the resulting model has been compared with sim-
pler null models and, when available, mechanistic alter-
natives. In this manuscript, EML is used as a generator
of candidate equations. The selected equations are then
read as one would typically, with terms for activation,
relaxation, and hidden coarse-grained states.
We define a simple yet useful EML-generated module,
M1(R) = eml(α ln R, eβR) = Rα − βR. (2)
This expression is a minimal candidate for adaptive or
biphasic responses: increasing input can initially increase
the output, while sufficiently strong input can suppress
it. Written in expanded form, the expression is more
readily interpretable than the EML notation itself. The
role of EML is to provide the compositional rule by which
this and higher-order modules are generated.
The well-known Hill functions remain an appropriate
null model for monotone saturating responses [11]. They
arXiv:2605.02972v1 [math.DS] 3 May 2026
2
are interpretable and widely used when modeling bio-
logical systems. The EML-generated module does not
attempt to replace them when they work. Its purpose is
to provide an alternative when the observed response is
nonmonotone, adaptive, or shaped by competing positive
and negative processes [12]. In such cases, a monotone
response function is insufficient, whereas our EML mod-
ule, Eq. 2, supports an internal optimum with a small
number of parameters.
Our central claim is methodological. The EML gate
is non-monotone in its argument with three parameters,
and is therefore the minimal activation-suppression block
that can produce a rise-then-fall response under mono-
tone input. Standard saturating primitives, e.g. the Hill
function, are monotone and require at least a difference
of two such blocks to produce the same shape. Building
on this depth-one structural asymmetry, we use EML
as a compact, differentiable, and recursively expandable
grammar for constructing reduced nonlinear ODEs: at
depth one it generates activation-suppression response
functions; at higher depth it generates cascades of hidden
states whose solutions are given by sequential convolution
integrals. We derive a controlled hierarchy of models in
which one can increase EML depth and ask whether the
additional structure is justified by held-out predictive er-
ror. Importantly, EML depth is not a count of molecular
steps; it is an effective coarse-grained dynamical depth,
useful when hidden delays or adaptive processes shape
the measured response.
This manuscript develops our methodology in three
steps. First, we apply an EML-ODE grammar to the
PKA regulatory-subunit relocalization data of LaCroix
et al. [13], who measured and then proposed a mechanis-
tic linker-occupancy model for the observed time-series.
The EML grammar is therefore tested as a surrogate, not
as a replacement for the known mechanism. Second, we
apply the restricted grammar to Rho-GTPase perturba-
tion data from Nanda et al. [14] and compare it directly
with a parallel Hill-grammar search of equal composi-
tional depth, making the depth-one asymmetry between
the two grammars concrete. Third, we construct a toy
high-dimensional activation-adaptation network and ask
whether a low-dimensional EML cascade can capture its
behavior.

</details>

# 2.results

<details>
<summary>2.resultの本文</summary>

We start from the activation-suppression module,
Eq. 2. Depending on the system, the suppression term
may represent sequestration, adaptation, toxicity, or an-
other process opposing the positive first term. For 0 <
α < 1 and β > 0, M1(R) is unimodal. The optimal in-
put is R∗ =
 α
β
1/(1−α)
, derived in Appendix A. Thus, a
monotonically increasing input can produce a transient
overshoot if it passes through the optimal point. This fea-
ture distinguishes the EML activation-suppression mod-
ule from a monotone Hill response, which can rise and
saturate or fall and saturate but cannot rise and then
fall under a monotone input without adding a second
term. The minimal time-dependent response model is a
first-order relaxation equation,
τ  ̇y = −y + y0 + BM1(R(t)),
= −y + y0 + B [R(t)α − βR(t)] . (3)
For chemically induced recruitment experiments, a useful
input model is
R(t) = R∞
1 − e−kR t , (4)
with R∞ proportional to the applied perturbation
strength. Equations (3) and (4) define a minimal
activation-suppression ODE. It has the convolution so-
lution (Appendix B),
y(t) = y(0)e−t/τ + 1
τ
Z t
0
e−(t−s)/τ [y0 + BM1(R(s))] ds.
(5)

</details>

# 2.A.EML as a symbolic-regression grammar

<details>
<summary>2.-A.EML as a symbolic-regression grammarの本文</summary>

The preceding equations can be read as an explicit re-
duced model, or, as the depth-one member of a restricted
EML expression grammar which defines our proposed
methodology. Below, we generate candidate models from
R(t), binary sums, and a centered EML gate
Ga,b,c(x) = emla ln[c + x], ebx − ca = (c + x)a − bx − ca.
(6)
The subtraction centers the gate at zero input and is
not a new mechanism; it fixes the baseline of the gen-
erated expression. The restricted grammar is specified
compactly as
E ::= R | G(E) | E + E. (7)
For the unfamiliar reader: the symbol E denotes a can-
didate expression; “::=” should be read as “is generated
as”; vertical bars “|” mean “or”. Thus, Eq. (7) says that a
candidate expression E may be one of three things: the
input variable R itself; an EML gate applied to a pre-
viously generated expression, G(E); or the sum of two
previously generated expressions, E + E. For example,
the grammar first allows R. Applying the second rule
gives G(R). Applying it again gives G(G(R)). Using
the addition rule gives expressions such as G(R) + R or
G(R)+G(R). Applying a gate to a sum gives expressions
such as G(G(R)+R). These are the expression trees that
are fitted and compared. To avoid duplicates, G(R) + R
and R+G(R) are treated as the same expression. A fitted
static response, i.e., an instantaneous algebraic mapping
without intrinsic relaxation time, has the form
y(t) = y0 + B E(R(t; k)), R(t; k) = 1 − e−kt. (8)
3
The search then enumerates all expressions satisfying
prescribed depth and node limits, fits their continuous
parameters by nonlinear least squares on training time-
series, and ranks models by held-out weighted error to-
gether with optional penalties on expression depth and
node count. For observations yi with standard errors σi,
training set T , and held-out set V, the fitted parameters
are
ˆθE = arg min
θ
X
i∈T
 yi − ˆyE (ti; θ)
 ̃σi
2
, (9)
where  ̃σi = max(σi, σfloor) prevents zero or very small
error values from dominating the fit. Model ranking uses
S(E) = 1
|V|
X
i∈V
"
yi − ˆyE (ti; ˆθE )
 ̃σi
#2
+ λdd(E) + λnn(E),
(10)
where d(E) is the EML depth and n(E) is the number
of expression-tree nodes. The fits shown here use λd =
λn = 0 and report the unpenalized held-out weighted
mean squared error; AIC and BIC are also computed as
diagnostic quantities but are not the primary selection
criterion. Although the model comparison can be done
differently, our methodological purpose is insensitive to a
precise comparison regime: EML is not the explanation
of a biological time-series. It is the engine used to propose
compact equations. Therefore, the empirical examples
below should be read as demonstrations of a constrained
model-discovery framework rather than as claims that
EML is a physical interaction law.
A natural comparator is a Hill recruitment response
H(R) = A Rh
Kh
d + Rh , (11)
with the corresponding relaxation model
τ  ̇y = −y + y0 + H(R(t)). (12)
Equation (12) is the correct null model when the per-
turbation produces a monotone approach to a saturated
activity. It is structurally inappropriate, however, for
recruitment-induced overshoot or biphasic responses, be-
cause H(R) is monotone in R for every choice of h > 0,
Kd > 0. Reproducing a rise-then-fall response from sat-
urating primitives therefore requires at least a difference
of two such blocks with opposing amplitudes, doubling
the static parameter count. By contrast, the centered
EML gate of Eq. (6) is non-monotone in x for 0 < a < 1,
b > 0 and produces an activation-suppression response
with a single block. This single-block non-monotonicity
is the structural asymmetry exploited in the experimen-
tal examples below, and we will return to it explicitly
when we compare the EML grammar to a Hill grammar
of equal compositional depth on the Nanda et al. data
(Sec. II C).

</details>

# 2.B.PKA-R relocalization in LaCroix et al.

<details>
<summary>2.-B.PKA-R relocalization in LaCroix et al.の本文</summary>

The first example is the PKA regulatory-subunit re-
localization experiment of LaCroix et al. [13], where
rapamycin-induced recruitment of PKA-R to the plasma
membrane produces a paradoxical response: low or inter-
mediate PKA-R recruitment enhances plasma-membrane
PKA activity, whereas high recruitment inhibits it. The
authors interpret this as a linker or scaffold-like stoichio-
metric effect. At moderate abundance, PKA-R helps as-
semble productive local signaling complexes; at excessive
abundance, it titrates cAMP or PKA-C away from pro-
ductive complexes and suppresses activity.
This dataset is useful because it has an independently
motivated mechanism, where signaling is proportional to
the concentration of fully occupied linker molecules [13].
A dynamical version of that model can be written as
τ  ̇yD = −yD + 1 + A [ΦN (SD (t)) − ΦN (S0)] , (13)
where SD (t) = S0 + qD(1 − e−kR t) and ΦN (S) denotes
the fully occupied linker concentration up to scale. For
the N = 4 case relevant to four cAMP-binding sites,
Φ4(S) = S
S4 + S3 + 2S2 + 3S + 4 . (14)
The derivation and normalization of Eq. (14) are sum-
marized in Appendix D.
We used this example to test whether the restricted
EML grammar can find a reduced surrogate. The search
used the same expression grammar as Eq. (7), but em-
bedded the selected expression in a first-order kinetic
equation rather than fitting it as an instantaneous static
response:
τ  ̇yD = −yD +1+B E(RD (t; k)), RD (t; k) = D(1−e−kt).
(15)
This kinetic embedding is important. A purely static
grammar, yD (t) = 1 + BE(RD (t)), can produce artifi-
cial early features because it forces PKA activity to fol-
low recruitment instantaneously. The relaxation form in
Eq. (15) removes that artifact and gives the grammar
the same minimal kinetic structure as the Hill and linker
comparators.
Figure 1 shows the resulting two-dose fit. The Hill
ODE remains structurally limited because it approaches
a dose-dependent monotone plateau. It therefore misses
the coexistence of a sustained low-dose response and a
transient high-dose response. The linker model gives an
excellent mechanistic description, as expected. The best
EML-grammar ODE selected from the restricted search
was
E∗(R) = G1(R) + G2(R), (16)
or, explicitly,
E∗(R) = (c1 + R)a1 − b1R − ca1
1 + (c2 + R)a2 − b2R − ca2
2 .
(17)
4
Thus, the grammar selected a sum of two centered one-
gate activation-suppression components sharing the same
recruitment variable. The numerical ordering should not
be overinterpreted: the EML expression has more fitted
parameters than the linker model, and the linker model
remains the mechanistically preferred description. The
important point is that a restricted EML grammar is
compatible with the known activation-suppression mod-
eling and clearly improves on the Hill null.

</details>

# 2.C.Grammar search on unresolved dynamics

<details>
<summary>2.-c.Grammar search on unresolved dynamicsの本文</summary>

The second example uses the Rho-GTPase recruitment
experiment of Nanda et al., in which constitutively active
Rho-family GTPases are acutely recruited to the plasma
membrane and downstream activity sensors are followed
over time [14]. Unlike the previous example, these data
are not accompanied by a compact model analogous to
the LaCroix linker equation. They are therefore a better
test of the methodological claim: EML as a grammar for
proposing and selecting reduced equations.
We applied the restricted grammar in Eq. (7) to the
perturbations in RhoA and Rac1 and resulting response
traces. The search was restricted to be small: expressions
were enumerated up to EML depth three and five total
expression-tree nodes, and continuous parameters were
fitted on training time points. Candidate models were
ranked by weighted error on held-out time points (Fig. 2).
Two features of this search are worth noting. First, even
at depth one the EML expression G(R) (green curve in
each panel) is already non-monotone and qualitatively
tracks the rise-and-fall of the data, in contrast to the Hill
comparator (orange) which saturates. A single Hill block
cannot rise and then fall under a monotone recruitment
input, whereas a single centered EML gate can. Second,
the same depth-2 expression G(G(R)+R) is selected as
the best held-out model for all four response traces. The
algorithm did not merely compare a manually chosen Hill
curve with a manually chosen EML curve; it searched a
small EML expression space and the same branching ex-
pression won across four physically distinct perturbation-
response combinations. We do not interpret this as a mi-
croscopic mechanism, but it does suggest that a common
compositional motif: input combined with delayed-and-
saturated input, then suppressed, captures the dominant
temporal structure of these responses.
To compare fairly with Hill-type modeling, we ran a
parallel grammar search in which the EML gate was re-
placed by a Hill block of the same form, E ::= R | H(E) |
E +E, with H(·) given by Eq. (11), and otherwise identi-
cal kinetic embedding, search bounds, and held-out val-
idation. The results are shown in Fig. 3. At depth one,
H(R) produces a monotone saturating curve in all four
panels, as expected, and visibly fails to capture the late-
time decay. The best Hill-grammar expression at depth
≤ 3 is H(R) + H(R) in all four panels, and matches
the EML fit in Fig. 2 closely. The qualitative picture
is therefore: at depth one, only the EML grammar pro-
duces a non-monotone response; at depth two, a sum of
two Hills [12] (with opposing amplitudes) reproduces the
EML fit. The EML grammar is not uniquely expressive,
but it does collapse a depth-2 Hill construction into a
depth-1 expression with fewer static-block parameters.
The asymmetry can be quantified using AIC and BIC
(Table S3 in Appendix C). At depth one, the EML gate
G(R) is preferred over the Hill block H(R) in every
panel by very large margins (∆AIC between 277 and
373, ∆BIC between 275 and 370), reflecting that no sin-
gle saturating block can fit the rise-then-fall shape. At
depth two, the comparison narrows: the EML expression
G(G(R)+R) (p = 9) achieves the lowest AIC and BIC
in panels (a), (c), and (d) despite carrying one more pa-
rameter than H(R) + H(R) (p = 8, with shared rate
constant), with ∆AIC of 27, 5.0, and 10.0 respectively. In
panel (b) the two grammars are essentially indistinguish-
able on held-out wMSE (0.0698 vs. 0.0737), and BIC’s
parsimony preference selects the simpler Hill. Both in-
formation criteria therefore confirm what the curves in
Fig. 2 and Fig. 3 suggest visually: at depth two the two
grammars are interchangeable in terms of fit quality, and
the EML choice is justified primarily by parsimony at
low depth and by the interpretability of each block as a
single activation-suppression unit.

</details>

# 2.D.A toy coarse-graining benchmark

<details>
<summary>2.-D.A toy coarse-graining benchmarkの本文</summary>

The grammar-search example above shows that EML
expressions can be selected from data, but it does not
demonstrate why higher EML depth could be useful. To
test this point, we constructed a toy high-dimensional
dynamical system whose output contains hidden delay
structure. The microscopic model has 50 internal states:
a fast activation branch with 20 first-order stages and a
slower inhibitory branch with 30 first-order stages. The
imposed input is again a monotone recruitment variable
R(t) = 1 − e−kR t. The measured output is a saturating
positive function of the terminal activation state minus
a saturating negative function of the terminal inhibitory
state. Thus the overshoot and later adaptation arise from
the separation of time scales in a high-dimensional net-
work, not from an EML construction. The full ODE
system used to generate the ground-truth trajectory is
given in Appendix G.
Can this 50-state input-output map be approximated
by a much lower-dimensional EML cascade? This bench-
mark was implemented in a reservoir-computing-like
form [15–17]. In this paradigm, a complex nonlinear dy-
namical system (the ’reservoir’) is kept fixed to generate
a rich set of temporal basis functions, and only a simple
linear readout layer is trained. By adopting this reser-
voir framework for our EML cascade, we treat the hidden
states as a fixed basis. Thus, the calculation did not re-
quire optimizing all ak, bk, ck, and τk parameters of a
deep nonlinear cascade. For this benchmark the EML
hidden states were generated by the centered cascade
τk  ̇zk = −zk + Gak ,bk ,ck (zk−1), z0(t) = R(t), (18)
with Ga,b,c defined in Eq. (6). The readout was not cho-
sen by hand. For each depth K, we fitted only a linear
output layer,
yK (t) = β0 +
KX
j=1
βj zj (t), (19)
on training time points and evaluated the prediction on
held-out time points. This makes the benchmark a con-
servative coarse-graining test: the EML cascade supplies
a fixed structured temporal basis, while only the out-
put weights are inferred from data. This choice reduces
computational cost, avoids deep nonlinear convergence
issues, and limits overfitting relative to fitting every cas-
cade parameter. The results are shown in Fig. 4. A
monotone Hill response fails because the target output is
generated by delayed activation followed by delayed in-
hibition. A one-state EML reduction is also insufficient.
However, the held-out weighted mean squared error de-
creases sharply with EML depth. The largest improve-
ment occurs between K = 1 and K = 2, indicating that
one hidden EML state cannot represent the delayed in-
hibitory component, whereas a second layer already cap-
tures much of the activation-adaptation structure. Be-
yond K = 6 the held-out wMSE plateaus, and AIC and
BIC both select K = 6 as the optimal depth (Table S4
in Appendix G); the additional layers K = 7, . . . , 10 re-
duce held-out wMSE only marginally and are penalized
by both information criteria.
This benchmark shows that EML depth can act as a
coarse-grained dynamical basis, not that it recovers the
microscopic species. Successive states z1, . . . , zK form
delayed pulse-like components generated from the same
monotone input, and the fitted readout combines these
components to approximate the output of a much larger
system. This is the operational meaning of higher-order
EML in the present framework: it is a controlled way to
increase reduced dynamical depth when hidden delays or
distributed adaptive processes are present.

</details>

# 2.E.Higher-order EML: solvable reduced ODE hierarchies

<details>
<summary>2.-E.Higher-order EML: solvable reduced ODE hierarchiesの本文</summary>

The LaCroix and Nanda examples use a first-order
grammar search, whereas the toy benchmark uses a cas-
cade of EML-generated states. The general construction
is triangular, meaning each layer depends only on the
output of the preceding layer, allowing the system to be
solved sequentially. Let z0(t) = R(t) and define
τ1  ̇z1 = −z1 + F1(z0), (20)
τk  ̇zk = −zk + Fk(zk−1), k = 2, . . . , K, (21)
where each drive is a centered EML gate
Fk(z) = (ck+z)ak −cak
k −bkz = eml(ak ln[ck+z], ebk z )−cak
k .
(22)
The subtraction of cak
k fixes the zero-input baseline, so
that downstream layers are driven only by upstream ac-
tivity. A measured response can then be modeled either
as a terminal output, yK (t) = zK (t), or as an observa-
tional readout
yK (t) = β0 +
KX
j=1
βj zj (t), (23)
as in the toy coarse-graining benchmark.
Equations (20–22) define a feedforward Hammerstein-
Wiener cascade with first-order linear blocks; the con-
tribution here is the use of the centered EML gate as
the static nonlinearity. Compared to standard choices
(sigmoid, Hill, polynomial), the EML gate provides
non-monotone activation-suppression with a closed-form
derivative. The hierarchy is exactly solvable:
zk(t) = zk(0)e−t/τk + 1
τk
Z t
0
e−(t−s)/τk Fk(zk−1(s)) ds.
(24)
Thus z1 is solved from the known input, z2 from z1,
and so on. General elementary closed forms are not ex-
pected for arbitrary K, but the convolution representa-
tion makes the reduced dynamics well defined and nu-
merically stable.
Linearization around a working point gives (Appendix E),
δ  ̇zk = − 1
τk
δzk+ gk
τk
δzk−1, gk = ak(ck+z∗
k−1)ak −1−bk.
(25)
The corresponding transfer function is
HK (s) =
KY
k=1
gk
1 + sτk
. (26)
Each additional layer therefore contributes one gain fac-
tor and one timescale. In this reduced sense, EML depth
is a model-selection parameter for hidden delay and adap-
tive structure, not a direct count of molecular regulatory
steps.

</details>

# 3.discussion

<details>
<summary>3.discussionの本文</summary>

The examples above suggest a narrow but useful role
for EML-generated ODEs as a model-discovery grammar.
The framework is best summarized by three claims.
First, the centered EML gate of Eq. (6) is a minimal
non-monotone activation-suppression block, whereas any
block built from monotone saturating primitives such as
the Hill function requires at least a difference of two such
blocks with opposing amplitudes to produce the same
shape. The Nanda et al. analysis (Fig. 2, Fig. 3) makes
this concrete: at depth one.
Second, at sufficient compositional depth other gram-
mars match EML. A Hill grammar at depth two repro-duces the EML fit on all four Nanda response traces using
a sum of two Hills with opposing amplitudes. The quan-
titative comparison in Sec. II C (AIC/BIC, Table S3)
shows that the depth-1 EML gate G(R) beats the depth-
1 Hill block H(R) by very large margins in all four pan-
els, while at depth two the two grammars become essen-
tially interchangeable, with EML preferred by AIC/BIC
in three panels and Hill preferred in the fourth. The EML
grammar is therefore not uniquely expressive in the limit
of unrestricted depth; its advantage is parsimony at low
depth and interpretability of the individual block as a
single activation-suppression unit.
Third, the centered EML cascade of Eqs. (20–22)
provides a controlled ladder between simple Hill-type
phenomenology and detailed mechanistic models. The
cascade is a feedforward Hammerstein-Wiener archi-
tecture in which model depth corresponds to hidden
activation-suppression regulatory depth; each additional
layer contributes one gain factor and one timescale to
the linearized transfer function (Eq. (26)). On the toy
benchmark this ladder compresses a 50-state activation-
adaptation network into a low-dimensional reservoir with
9
a learned linear readout. AIC and BIC both select K = 6
as the optimal cascade depth (Table S4), one depth be-
low the held-out wMSE plateau, identifying an effective
coarse-grained dimensionality of six for this network.
When an established mechanism exists, as in the PKA-
R linker model [13], the mechanistic model is preferable.
The EML model is valuable there because it demon-
strates that a one-gate activation-suppression module
recovers a real biochemical response motif at held-out
wMSE comparable to the linker model, even though the
linker model is the mechanistically preferred description.
Several limitations are immediate. First, as the Hill-
grammar comparison shows, the EML hierarchy is not
uniquely expressive; other grammars can generate bipha-
sic and adaptive responses at modestly higher composi-
tional depth. Second, the biological interpretation of ak,
bk, and ck is reduced-model interpretation, not direct
molecular measurement unless additional experiments
constrain the underlying processes. Third, increasing K
can overfit unless penalized by predictive validation or in-
formation criteria such as AIC or BIC (Appendix F). Se-
lection in this manuscript uses held-out wMSE as the pri-
mary criterion; AIC and BIC are reported alongside (Ta-
bles S3 and S4) and broadly confirm the held-out wMSE
rankings, with the one exception of Nanda panel (b)
noted above. These limitations are not defects specific
to EML; they are the usual constraints on reduced dy-
namical modeling.
The proposed value of EML is that it organizes model
expansion and symbolic regression. Instead of adding ar-
bitrary empirical terms until a curve is fit, one increases
EML depth and asks whether the data justify another
activation-suppression layer. If the answer is no, the
first-order model is sufficient. If the answer is yes, the
added layer has a clear dynamical interpretation and an
exact convolution solution. This makes EML-generated
ODEs a plausible grammar for model discovery in sys-
tems where perturbations induce overshoot, adaptation,
or biphasic responses but a detailed mechanistic model
is unavailable.
The universality of EML is a risk as well as a strength.
Without a restricted grammar and explicit penalties,
EML can generate arbitrary curve-fitting expressions.
The framework is therefore meaningful only when the al-
lowed terminals, EML depth, parameter count, and val-
idation procedure are specified in advance. In an era in-
creasingly dominated by opaque machine learning mod-
els, EML offers a mathematically transparent bridge be-
tween data-driven discovery and interpretable nonlinear
dynamics.

</details>

# 4.acknowledgments

<details>
<summary>4.acknowledgmentsの本文</summary>

Numerical simulations were paid for by AE’s startup
funds.
Data availability
All scripts, processed inputs, and commands required
to reproduce the figures are available at https://www.
github.com/AmirErez/Manuscript_EML_biophysics.
[1] Mark K. Transtrum, Benjamin B. Machta, Kevin S.
Brown, Bryan C. Daniels, Christopher R. Myers, and
James P. Sethna. Perspective: Sloppiness and emergent
theories in physics, biology, and beyond. The Journal of
Chemical Physics, 143(1):010901, July 2015.
[2] Jamie A. Lopez and Amir Erez. Mathematical Mod-
elling and Intuition in Microbiology: A Perspective. En-
vironmental Microbiology, 28(4):e70266, 2026. e70266
1612994.
[3] Philip Nelson. Physical Models of Living Systems:
Probability, Simulation, Dynamics. Chiliagon Science,
Philadelphia, PA, 2022.
[4] Michael Schmidt and Hod Lipson. Distilling Free-
Form Natural Laws from Experimental Data. Science,
324(5923):81–85, April 2009.
[5] Silviu-Marian Udrescu and Max Tegmark. AI Feynman:
A physics-inspired method for symbolic regression. Sci-
ence Advances, 6(16):eaay2631, April 2020.
[6] Miles Cranmer, Alvaro Sanchez Gonzalez, Peter
Battaglia, Rui Xu, Kyle Cranmer, David Spergel, and
Shirley Ho. Discovering Symbolic Models from Deep
Learning with Inductive Biases. In Advances in Neu-
ral Information Processing Systems, volume 33, pages
17429–17442. Curran Associates, Inc., 2020.
[7] Bryan C. Daniels and Ilya Nemenman. Automated adap-
tive inference of phenomenological dynamical models.
Nature Communications, 6(1):8133, August 2015.
[8] Steven L. Brunton, Joshua L. Proctor, and J. Nathan
Kutz. Discovering governing equations from data
by sparse identification of nonlinear dynamical sys-
tems. Proceedings of the National Academy of Sciences,
113(15):3932–3937, April 2016.
[9] Samuel H. Rudy, Steven L. Brunton, Joshua L. Proctor,
and J. Nathan Kutz. Data-driven discovery of partial
differential equations. Science Advances, 3(4):e1602614,
April 2017.
[10] Andrzej Odrzywolek. All elementary functions from a
single binary operator. arXiv:2603.21852 [cs.SC], 2026.
https://arxiv.org/abs/2603.21852.
[11] HILL A. V. The possible effects of the aggregation of
the molecules of hemoglobin on its dissociation curves.
J. Physiol., 40:iv–vii, 1910.
[12] Robert M. Vogel, Amir Erez, and Gr ́egoire Altan-Bonnet.
Dichotomy of cellular inhibition by small-molecule in-
hibitors revealed by single-cell analysis. Nature Com-
munications, 7(1):12428, September 2016.
[13] Rebecca LaCroix, Benjamin Lin, Tae-Yun Kang, and An-
dre Levchenko. Complex effects of kinase localization
revealed by compartment-specific regulation of protein
kinase A activity. eLife, 11:e66869, February 2022.
[14] Suchet Nanda, Abram Calderon, Arya Sachan, Thanh-
Thuy Duong, Johannes Koch, Xiaoyi Xin, Djamschid
10
Solouk-Stahlberg, Yao-Wen Wu, Perihan Nalbant, and
Leif Dehmelt. Rho GTPase activity crosstalk mediated
by Arhgef11 and Arhgef12 coordinates cell protrusion-
retraction cycles. Nature Communications, 14(1):8356,
December 2023.
[15] Wolfgang Maass, Thomas Natschl ̈ager, and Henry
Markram. Real-Time Computing Without Stable States:
A New Framework for Neural Computation Based on
Perturbations. Neural Computation, 14(11):2531–2560,
November 2002.
[16] Herbert Jaeger and Harald Haas. Harnessing Nonlin-
earity: Predicting Chaotic Systems and Saving Energy
in Wireless Communication. Science, 304(5667):78–80,
April 2004.
[17] Kohei Nakajima. Physical reservoir computing—an in-
troductory perspective. Japanese Journal of Applied
Physics, 59(6):060501, May 2020.

</details>