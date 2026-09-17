---
source: null
title: "review-candidate-1402"
page_count: 8
converted_at: "2026-09-06T01:02:08Z"
---

<!-- PDF_PAGE: 1 -->

<div align="center">

# Fuzzy Classification Context for the Responsive and Formal Design Process

</div>

Solomon Gebreyohannes, William Edmonson, Albert Esterline, Abdollah Homaifar, and Nadew Kibret

NC A & T State University

Greensboro, NC 27411

Email: shgebrey@aggies.ncat.edu, {wwedmons,esterlin,homaifar}@ncat.edu, nskibret@aggies.ncat.edu

Abstract—This paper presents an application of a fuzzy relation in system modeling (from requirements) to be used for a Systems Engineering (SE) methodology. We define fuzzy classifications (models for distributed systems), extract component and system theories (sets of logical expressions), and ensure consistency of requirements for the Responsive and Formal Design (RFD) Process. The RFD process is a SE methodology that relates a set of requirements, associated models, simulations, and the relationship between them, by integrating Model-Based Systems Engineering (MBSE) to manage system modeling complexity with formal methods to ensure that designs are verifiably correct against their requirements. To translate informal requirements to logical expressions in the RFD process, we first model requirements using a 3-tuple structure called a classification formulated from Barwise and Seligman's channel theory. A classification consists of "tokens" (observed situations) and "types" (situation features) and a binary relation classifying tokens with types. However, classifying tokens using types as present (represented as '1') or absent (represented as '0') as used in channel theory is not always possible (since it involves vagueness and imprecision) and the representation lacks expressiveness to reason about relations among such types (vague situation features). Hence, a binary classification doesn't capture uncertainity. In this paper, we consider a degree of truth in the relation between tokens and types to define a fuzzy classification. We then develop an algorithm that extracts a theory from a fuzzy classification. This helps in formal proof for checking consistency (no contradiction) and deducing to requirements (verifying properties). We demonstrate our development using three small satellites measurement system whose goal is to image the colorful auroral ovals seen around Earth's magnetic poles.

## I. INTRODUCTION

This paper is a continuation of our work on the Responsive and Formal Design (RFD) process. The RFD process is developed as a procedure used in designing engineered systems [1], [2]. It relates a set of requirements, associated models, simulations, and the relationship between them, by integrating Model-Based Systems Engineering (MBSE) [3] to manage system modeling complexity with formal methods [4] to ensure that designs are verifiably correct against their requirements. A major benefit of the RFD is the integration of formal methods throughout the design process as an integral part of requirements management, with the goal of insuring that the engineered product represents a high-confidence system. System requirements expressed in natural language is the starting point of any design process, for the RFD process in particular. We then model the system (from the given requirements) using a 3-tuple structure called a classification,

formulated from Barwise and Seligman's channel theory [5], [6]. A classification consists of a set of objects to be classified called "tokens" (observed situations), a set of objects used to classify the tokens called "types" (situation features), and a binary relationship between them. It is usually presented using a table with entries 0 and 1. However, modeling a distributed system using a classification (and its logical representation called a theory) based on a binary relation between tokens and types is not always possible, since it involves vagueness and imprecision. The representation lacks expressiveness to reason about relations among such types (vague situation features). This in turn limits the expressiveness of the simulation (of the model) and hence the design process as a whole. Defining a classification and a theory over a fuzzy set of types considers uncertainty and delivers rich expressiveness. A fuzzy set is a set whose elements have degrees of membership [7]. An approach to computing on fuzzy sets (fuzzy logic) is closer to human or natural reasoning. Fuzzy relations have been applied in widespread and important applications.

In this paper, therefore, we present an application of a fuzzy relation in system modeling (from requirements) to be used for a Systems Engineering (SE) methodology. We define a fuzzy classification and extract a theory to check consistency and deduce to a requirement. A fuzzy classification defines the relation between tokens and types over [0,1]. This means that a given token has a type with a given degree of truth; e.g., a has types $ \{\alpha, \beta, \gamma\} $ with degree of truth 0.9, 1.0, and 0.7, respectively. This can be written as $ \left\{ \begin{array}{l l} 0. 9 / \alpha , \beta , 0. 7 / \gamma \end{array} \right\} $ and interpreted as: "it is almost true that a has types $ \{\alpha, \beta, \gamma\} $ ". A set of logical expressions called a theory can be extracted from a classification. A theory is a set of sequents (pairs of sets of types) $ \langle \Gamma, \Delta \rangle $ such that $ \Gamma \vdash \Delta $ where $ \Gamma $ and $ \Delta $ are (fuzzy) collections of types. The relation $ \vdash $ is called (Gentzen) consequence relation or entailment and the formula is interpreted as: "each token having all types from $ \Gamma $ has some types from $ \Delta $ ". Unlike informal requirements, the logical expressions help in formal proofs for checking consistency (no contradiction) and deducing to requirements (verifying properties). We develop an algorithm that extracts a theory (a set of entailment formulas) from a fuzzy classification (based on our algorithm for a binary classification [8]). Then, we show how to derive (based on structural rules or Armstronglike rules [9]) requirements from a theory following proof procedures.

<!-- PDF_PAGE: 2 -->

Similar but stricter formulas (that extract fewer constraints from the same system) for a binary data table have been studied in computer science and mathematics; e.g., implications [10] -[13] and functional dependencies [9], [14], [15]. These formulas have also been studied for fuzzy sets. Implication formulas (and related concepts and analysis) using fuzzy sets are presented in [16] -[25]. Similarly, functional dependencies using fuzzy sets are discussed in [26]. However, there is no, to our knowledge, any other work that presents extraction of entailment formulas from a classification (or similar data table) for a fuzzy case. In [27], a graded approach of information flow is presented, but it does not include theory extraction or its application to systems engineering.

The rest of the paper is organized as follows. Section II introduces Barwise and Seligman's channel theory for modeling distributed systems. It also presents preliminaries on fuzzy sets and fuzzy logic along with definition of a fuzzy classification, entailment, sequent, partition, and theory. Section III introduces the RFD process and presents the formal framework of requirements management for the RFD process based on channel theory. In Section IV, we develop an algorithm that extracts a theory from a fuzzy classification. This section also presents how to define, achieve, and show consistency within a fuzzy classification. In Section V, we use an example of data from three small satellites, whose goal is to image the auroral ovals around Earth's magnetic poles, to demonstrate our development on formal requirement verification. Section VI concludes this paper.

## II. CHANNEL THEORY AND FUZZY CLASSIFICATION

This section introduces channel theory and defines a fuzzy classification, entailment, sequent, partition, and theory.

## A. Channel Theory

Barwise and Seligman [5], [6] presented a framework for the "flow of information" in category-theoretic terms. They address the question, "How is it that information about any component of a system carries information about other components of the system?" A notion of a classification is used to represent information networks. It is usually presented using a table.

Definition 2.1: [6] (p. 69) A classification $ \mathcal{A}= $ $ \langle tok(\mathcal{A}),typ(\mathcal{A}),\models_{\mathcal{A}}\rangle $ consists of

- a set, $ tok(\mathcal{A}) $ , of objects to be classified, called the tokens of $ \mathcal{A}. $

- a set, typ( $ \mathcal{A} $ ), of objects used to classify the tokens, called the types of $ \mathcal{A} $ , and

- a binary relation, $ \models_{\mathcal{A}} $ , between $ tok(\mathcal{A}) $ and $ typ(\mathcal{A}) $ .

For classifications $ \mathcal{A} $ and $ \mathcal{C} $ , an infomorphism $ f $ from $ \mathcal{A} $ to $ \mathcal{C} $ is a pair of functions $ (f^{\wedge},f^{\vee}) $ , where $ f^{\wedge}:typ(\mathcal{A})\rightarrow typ(\mathcal{C}) $ and $ f^{\vee}:tok(\mathcal{C})\rightarrow tok(\mathcal{A}) $ , satisfying, for all tokens $ c\in tok(\mathcal{C}) $ and all types $ \alpha\in typ(\mathcal{A}) $ , $ f^{\vee}(c)\models_{\mathcal{A}}\alpha $ iff $ c\models_{\mathcal{C}}f^{\wedge}(\alpha) $ . In category theoretic terms, an informorphism is a kind of Galois connection. A contravariant Galois connection between $ (tok(\mathcal{A}),typ(\mathcal{A}),\models_{\mathcal{A}}) $ and $ (tok(\mathcal{B}),typ(\mathcal{B}),\models_{\mathcal{B}}) $ will be a pair $ (\varphi,\psi) $ of mappings

$ \varphi : tok(\mathcal{A})\longrightarrow typ(\mathcal{B}),\psi : tok(\mathcal{B})\longrightarrow typ(\mathcal{A}) $ satisfying $ a\models_{\mathcal{A}}\psi(b) $ if and only if $ b\models_{\mathcal{B}}\varphi(a). $ An infomorphism between $ (tok(\mathcal{A}),typ(\mathcal{A}),\models_{\mathcal{A}}) $ and $ (tok(\mathcal{B}),typ(\mathcal{B}),\models_{\mathcal{B}}) $ however is a covariant Galois connection. There is a contravariant Galois connection between $ (tok(\mathcal{A}),typ(\mathcal{A}),\models_{\mathcal{A}}) $ and $ (typ(\mathcal{B}),tok(\mathcal{B}),\models_{\mathcal{B}}^{-1}) $ where $ \models_{\mathcal{B}}^{-1}\subseteq typ(\mathcal{B})\times tok(\mathcal{B}) $ with $ (\beta,b)\in\models_{\mathcal{B}}^{-1} $ iff $ (b,\beta)\in\models_{\mathcal{B}}. $

An information channel is a family of infomorphisms with a common codomain, called the core. Essentially, a channel consists of a set $ \mathcal{A}_{1},\dots, \mathcal{A}_{n} $ of classifications that represent the parts of the distributed system, a classification $ \mathcal{C} $ (the core) that represents the system as a whole, and a set of infomorphisms $ f_{1},\dots,f_{n} $ from each of the parts onto $ \mathcal{C} $ . Tokens in $ \mathcal{C} $ are the connections of the system: a given token c in $ \mathcal{C} $ connects the tokens it is related to by means of $ f_{1},\dots,f_{n} $ . Parts $ \mathcal{A}_{1},\dots, \mathcal{A}_{n} $ carry information about each other as long as they all are parts of $ \mathcal{C} $ . Intuitively, an information channel is a part-to-whole $ \mathcal{A}_{i} $ to- $ \mathcal{C} $ informational relationship. In category theoretic terms, the core is a cocone in the category of classifications (objects are classifications and morphisms are informorphisms).

Turning to regularities in a classification's types, let $ \mathcal{A} $ be a classification and $ \Gamma $ and $ \Delta $ be subsets of types in $ \mathcal{A} $ . Recall that a token a of $ \mathcal{A} $ satisfies the sequent $ \Gamma \vdash \Delta $ given that, if a is a token of every type in $ \Gamma $ , then it is of some type in $ \Delta $ . If every token of $ \mathcal{A} $ satisfies $ \Gamma \vdash \Delta $ , then $ \Gamma $ is said to entail $ \Delta $ and $ \Gamma \vdash \Delta $ is called a constraint supported by $ \mathcal{A} $ . The set of all constraints supported by $ \mathcal{A} $ is called the complete theory of $ \mathcal{A} $ , denoted by $ Th(\mathcal{A}) $ . These constraints are systematic regularities, and it is by virtue of regularities among connections that information about certain components of a distributed system can be carried by other components into diverse parts of the system. Barwise and Seligman's summary statement of their analysis of information flow, restricted to the simple case of a system with two components, is as follows: "Suppose that the token a is of type $ \alpha $ . Then a's being of type $ \alpha $ carries the information that b is of type $ \beta $ , relative to channel C, if a and b are connected in C and if the translation $ \beta^{\prime} $ of $ \beta $ entails the translation $ \alpha^{\prime} $ of $ \alpha $ in the theory $ Th(\mathcal{C}) $ where $ \mathcal{C} $ is the core of C" [6].

Finally, a theory is regular if it satisfies

Identity: $ \alpha\vdash\alpha, $

Weakening: If $ \Gamma\vdash\Delta, $ then $ \Gamma, \Gamma^{\prime}\vdash\Delta, \Delta^{\prime}, $

Global Cut: If $ \Gamma, \Sigma_{0}\vdash\Delta, \Sigma_{1} $ then $ \Gamma\vdash\Delta, $

where $ \Gamma, \Delta $ , and $ \Sigma $ are subsets of types of a classification and $ \langle \Sigma_{0},\Sigma_{1}\rangle $ is a partition. A sequent $ \langle \Gamma, \Delta \rangle $ of $ \Sigma $ is a partition if $ \Gamma \cup \Delta=\Sigma $ and $ \Gamma \cap \Delta=\emptyset $ . Transitivity: For any type $ \alpha $ , if $ \Gamma\vdash\alpha $ and $ \alpha\vdash\Delta $ , then $ \Gamma\vdash\Delta $ .

## B. Fuzzy Classification

1) Fuzzy Logic and Sets Preliminaries: This section introduces fuzzy logic and fuzzy sets, following [28] - [35]. A residuated lattice in an abstract algebra is defined as:

Definition 2.2: A (complete) residuated lattice with a truth stressing hedge is an algebra $ L=\langle L,\wedge ,\vee ,\otimes ,\rightarrow ,\ast ,0,1\rangle $ such

<!-- PDF_PAGE: 3 -->

that $ \langle L,\wedge ,\vee ,0,1\rangle $ is a (complete) lattice with 0 and 1 the least and greatest element of L, respectively, $ \langle L,\otimes ,1\rangle $ is a commutative monoid $ (x\otimes 1=1\otimes x=x,x\in L) $ , and $ \otimes $ (multiplication) and $ \rightarrow $ (residuum) satisfying the adjointness property: $ x\otimes y\leq z $ iff $ x\leq y\rightarrow z $ $ (x,y,z\in L) $ . In addition to that, $ \ast : L\to L $ (a hedge) satisfies $ 1^{*} = 1 $ $ x^{*} \leq x $ $ (x\rightarrow y)^{*} \leq x^{*} \rightarrow y^{*} $ , and $ x^{**}=x^{*} $ $ (x,y\in L) $ [22], [29], [33].

Note that $ \otimes $ and $ \rightarrow $ are truth functions of "fuzzy conjunction" and "fuzzy implication".

A common choice of L are ( [22], [24]):

1) L = [0,1] unit interval

2) Connectives:

i $ \wedge $ : Minimum

ii V:Maximum

3) Fuzzy conjunction $ \otimes $:

i Lukasiewicz: $ x\otimes y=max(x+y-1,0), $

ii Godel: $ x\otimes y=min(x,y), $

iii Goguen: $ x\otimes y=x\cdot y. $

## 4) Fuzzy implication $ \rightarrow $:

i Lukasiewicz: $ x \rightarrow y=min(1-x+y,1) $

ii Godel:

$$
x \rightarrow y = \left\{\begin{array}{l l}1,&\mathrm {i f} x \leq y\\y,&\mathrm {o t h e r w i s e}\end{array}\right.
$$

iii Goguen:

$$
x \rightarrow y = \left\{\begin{array}{l l}1,&\text {if} x \leq y\\\frac {y}{x},&\text {o t h e r w i s e}\end{array}\right.
$$

5) Two boundary cases of (truth-stressing) hedges are [22]:

i Identity $ x^{*} = x $ $ (x\in L) $

ii Globalization $ x^{*} = 1 $ if $ x=1 $ and 0 otherwise.

An $ L $ - set (fuzzy set) is defined as:

Definition 2.3: A fuzzy set [7], [36] is characterized by a membership function mapping the elements of a domain, space, or universe of discourse U to the interval [0,1]. For a fuzzy set $ \Gamma $ $ \Gamma: U $ [0,1].

For the universe of discourse $ U=\{u_{1},u_{2},\dots,u_{n}\} $ , a fuzzy set $ \Gamma $ can be represented as $ \Gamma=\{\gamma_{1}/u_{1},\dots,\gamma_{n}/u_{n}\} $ meaning that $ \Gamma(u_{i})=\gamma_{i} $ for each $ i=1,\dots,n. $ Now, we define the degree to which a fuzzy set $ \Gamma $ is contained in a fuzzy set $ \Sigma $ i.e. subsethood.

Definition 2.4: Given $ \Gamma $ and $ \Sigma $ , a subsethood degree can be defined as [22], [37]:

$$
S (\Gamma , \Sigma) = \bigwedge_ {u \in U} (\Gamma (u) \rightarrow \Sigma (u)).
$$

which generalizes the classical subsethood relation $ \subseteq. $ $ S(\Gamma ,\Sigma) $ represents a degree to which $ \Gamma $ is a subset of $ \Sigma. $ If $ S(\Gamma ,\Sigma)=1, $ $ \Gamma $ is fully contained in $ \Sigma $ and written as $ \Gamma \subseteq \Sigma. $

2) Fuzzy Classification and Theory: In modeling distributed systems using channel theory, Barwise and Seligman define a classification using a binary relation (presence or absence) between tokens and types i.e. a given token either fully contains a type (represented as '1') or it doesn't (represented as '0') [6]. In this section, we define a fuzzy classification

enabling degree of truth (or adding uncertainty) and use to model components and the whole system.

Definition 2.5: A fuzzy classification $ \mathcal{A} $ = $ \langle tok(\mathcal{A}), typ(\mathcal{A}), \models_{\mathcal{A}} \rangle $ consists of

- a set, $ tok(\mathcal{A}) $ , of objects to be classified, called the tokens of $ \mathcal{A} $ .

- a set, typ( $ \mathcal{A} $ ), of objects used to classify the tokens, called the types of $ \mathcal{A} $ , and

- $ \models_{\mathcal{A}} \in L^{tok(\mathcal{A}) \times typ(\mathcal{A})} $ is a binary relation between $ tok(\mathcal{A}) $ and $ typ(\mathcal{A}) $ assigning to each token $ a \in tok(\mathcal{A}) $ and each type $ \alpha \in typ(\mathcal{A}) $ a degree $ \models_{\mathcal{A}} (a, \alpha) \in L=[0,1] $ to which a has $ \alpha. $

Combining classifications gives a way of putting the components of the information channel together into a single classification (the same is true for combining the infomorphisms). This simplifies finding of the logic that captures the constraints of the system [6]. The most basic way of combining classifications is to add them. In adding classifications $ \mathcal{A}_{1},\mathcal{A}_{2},\dots $ and $ \mathcal{A}_{n} $ , we classify tuples $ \langle a,b,\dots,n\rangle $ of tokens, a from $ \mathcal{A}_{1} $ b from $ \mathcal{A}_{2},\dots $ , and n from $ \mathcal{A}_{n} $ , using types that are copies of the types in $ \mathcal{A}_{1},\mathcal{A}_{2},\dots $ , and $ \mathcal{A}_{n} $ .

Definition 2.6: (cf. Definition 5.5, p. 83 [6] for binary classifications) Given fuzzy classifications $ \mathcal{A}_{1},\mathcal{A}_{2},\dots,\mathcal{A}_{n} $ the sum

$$
\mathcal {A} = \sum_ {i \in \{1, \dots , n \}} \mathcal {A} _ {i} = \mathcal {A} _ {1} + \mathcal {A} _ {2} + \dots + \mathcal {A} _ {n}
$$

f $ \mathcal{A}_{1},\mathcal{A}_{2},\dots $ , and $ \mathcal{A}_{n} $ is the classification defined as follows: The set $ tok(\mathcal{A}_{1}+\mathcal{A}_{2}+\dots+\mathcal{A}_{n}) $ is the Cartesian product of $ tok(\mathcal{A}_{1}),tok(\mathcal{A}_{2}),\dots $ , and $ tok(\mathcal{A}_{n}). $ Specifically, the tokens of $ \mathcal{A}_{1}+\mathcal{A}_{2}+\dots+\mathcal{A}_{n} $ are tuples $ \langle a,b,\dots,n \rangle $ of tokens, $ a\in tok(\mathcal{A}_{1}),b\in tok(\mathcal{A}_{2}),\dots $ , and $ n\in tok(\mathcal{A}_{n}). $

- The set $typ(\mathcal{A}_1 + \mathcal{A}_2 + \dots + \mathcal{A}_n)$ is the disjoint union of $typ(\mathcal{A}_1)$, $typ(\mathcal{A}_2)$, $ \cdots $ , and $typ(\mathcal{A}_n)$.

- The classification relation $ \models_{\mathcal{A}_{1}+\mathcal{A}_{2}+\dots+\mathcal{A}_{n}} $ is defined by $ a_{1}, a_{2}, \dots, a_{n} \models_{\mathcal{A}_{1}+\mathcal{A}_{2}+\dots+\mathcal{A}_{n}} \langle i, \alpha \rangle $ if $ a_{i} \models_{\mathcal{A}_{i}} \alpha, \forall i \in $ {1,2,…,n}.

We define a (Gentzen) consequence relation, or entailment $ \vdash $ to study the relations among the types (situation features) of a classification (a set of situations). For $ \Gamma, \Delta \in \mathbf{L}^{typ(\mathcal{A})} $ , the intended meaning of the formula $ \Gamma\vdash\Delta $ is: "each token of the classification A having all types from $ \Gamma $ has some types from $ \Delta $ ". The degree to which $ \Gamma\vdash\Delta $ is valid in a fuzzy set of types represented by a token, say token a, is given by $ \| \Gamma\vdash\Delta \|_{a} $ [27].

$$
\| \Gamma \vdash \Delta \| _ {a} = S ^ {*} (\Gamma , a) \rightarrow \bigvee_ {\alpha \in t y p (\mathcal {A})} a (\alpha) \otimes \Delta (\alpha)
$$

where $ \ast $ and $ \rightarrow $ are truth stressing hedge and fuzzy implication respectively.

Now, we define a degree $ \| \Gamma\vdash\Delta\|_{\mathcal{A}}\in L $ to which $ \Gamma\vdash\Delta $ is valid in a classification $ \mathcal{A} $ by:

$$
\| \Gamma \vdash \Delta \| _ {\mathcal {A}} = \bigwedge_ {a \in t o k (\mathcal {A})} \| \Gamma \vdash \Delta \| _ {a}
$$

As a particular example,

<!-- PDF_PAGE: 4 -->

- If $ \| \Gamma\vdash\Delta\|_{\mathcal{A}}=1 $ means that a proposition "for each token a $ \in tok(\mathcal{A}) $ : if for each type $ \alpha\in typ(\mathcal{A}) $ , a has $ \alpha $ in degree greater than or equal to (a threshold) $ \Gamma(\alpha) $ then for some $ \alpha\in typ(\mathcal{A}) $ , a has $ \alpha $ in degree at least $ \Delta(\alpha) $ " is true.

- If $ \Gamma(\alpha)=\gamma $ for $ \alpha\in\Sigma\subseteq typ(\mathcal{A}) $ (and $ \Gamma(\alpha)=0 $ for $ \alpha\notin\Sigma) $ $ \Delta(\alpha)=\delta $ for $ \alpha\in\Sigma^{\prime}\subseteq typ(\mathcal{A}) $ (and $ \Delta(\alpha)=0 $ for $ \alpha\notin\Sigma^{\prime}) $ , the proposition says "for each token $ a\in $ tok( $ \mathcal{A} $ ): if a has all types from $ \Sigma $ in degree at least $ \gamma $ then a has some types from $ \Sigma^{\prime} $ in degrees at least $ \delta $ , etc.

Similarly, a sequent and partition can be defined as:

$$
\Gamma , \Delta , \Sigma \in \mathbf {L} ^ {t y p (\mathcal {A})}
$$

$$
\mathcal {A})
$$

$$
\langle \Gamma , \Delta \rangle
$$

$$
\sum
$$

$$
S (\Gamma , \Sigma) \otimes S (\Delta , \Sigma)
$$

The subsethood degree of $ \Gamma $ in $ \Sigma $ is $ S(\Gamma ,\Sigma) $ and that of $ \Delta $ in $ \Sigma $ is $ S(\Gamma ,\Delta) $ . We combine the subsethood degrees using fuzzy conjunctive $ \otimes $ to find the subsethood of the pair $ \langle \Gamma ,\Delta \rangle $ in $ \Sigma $ , that is $ S(\Gamma ,\Sigma)\otimes S(\Delta ,\Sigma) $ .

Definition 2.8: For $ \Gamma, \Delta, \Sigma\in\mathbf{L}^{typ(\mathcal{A})} $ (L-set of types of $ \mathcal{A} $), a sequent $ \langle\Gamma, \Delta\rangle $ is a partition of a fuzzy set $ \Sigma $ if $ \forall\alpha, \alpha\in $ $ typ(\mathcal{A}), (\Gamma\cup\Delta)(\alpha)=\Sigma(\alpha) $ and $ (\Gamma\cap\Delta)(\alpha)=0. $

In logic, a theory is considered as a collection of formulas. In fuzzy logic, a theory $ T $ can be considered as a fuzzy set of formulas [18], [22]. For each formula $ r_{i}, i\leq I, I\in \mathbb{N} $ in a theory, a degree $ T(r_{i}) $ to which $ r_{i} $ belongs to $ T $ is the degree in which $ r_{i} $ is valid.

Definition 2.9: For a given fuzzy set $ \Sigma $ and a fuzzy consequence relation $ \vdash $ on $ \Sigma $ , a theory is a pair $ T=\langle\Sigma,\vdash\rangle $

Definition 2.10: A constraint of the theory $ T $ (with a given degree $ \gamma $ ) is a sequent $ \langle \Gamma ,\Delta \rangle $ of $ \Sigma $ for which, $ \Gamma \vdash \Delta $ with at least $ \gamma $ degree of validity.

In general, we deal with a fuzzy set of formulas T with corresponding degree of validity. Sometimes, we use only sets of formulas T with fully true degree of validity.

## III. FORMAL REQUIREMENTS MANAGEMENT IN THE RESPONSIVE AND FORMAL DESIGN PROCESS

## A. The Responsive and Formal Design Process

The RFD process is developed as a procedure used in designing systems. It combines MBSE to manage system modeling complexity and formal methods [4] to ensure that designs are verifiably correct against their requirements. The integration of formal methods throughout the design process as an integral part of requirements management provides a high-confidence system which is the goal of the RFD process. The framework which we follow in implementing this RFD process is based on mission design flow [38], and is iterative. We introduced the RFD process in [1], [2]. We also showed integrating the RFD process with standard frameworks like the Open-System Interconnection (OSI) framework in [39].

Designing a system using a short and agile process relies on the ability to characterize system function at various levels of abstraction [40]. The RFD process consists of different levels of abstraction. Each level $ \mathcal{A}_{i} $ (the $ i^{th} $ level) consists of the behavior (specification), $ \mathcal{M}_{B}^{i} $ , and parametric (realization), $ \mathcal{M}_{p}^{i} $ , parts and represents a set of requirements and its

associated models, simulations, and the relationships between them. A similar way of grouping parts in a (categorical) design process model is also presented in [41] (and more in [42]) as specification and realization parts. The illustration below summarizes the essence of the RFD process.

$$
\mathcal {A} _ {i}: \begin{array}{c c c} \mathcal {M} _ {B} ^ {i}: \text {B e h a v i o r a l p a r t} \\ \mathcal {L} _ {n} ^ {i} \Longleftrightarrow \mathcal {L} _ {l} ^ {i} \\ \Downarrow \\ \mathcal {S} _ {b} ^ {i} \end{array} \Longleftrightarrow \begin{array}{c c c} \mathcal {M} _ {P} ^ {i}: \text {P a r a m e t r i c p a r t} \\ \mathcal {M} ^ {i} \Longrightarrow \mathcal {S} _ {p} ^ {i} \end{array}
$$

where design parameters are defined as:

- $ \mathcal{L}_{n}^{i}\Rightarrow $ requirements written in natural language form,

- $ \mathcal{L}_{l}^{i}\Rightarrow $ requirements written as a set of logical expressions,

- $ \mathcal{M}^{i}\Rightarrow $ system of interconnected models,

- $ \mathcal{S}_{p}^{i}\Rightarrow $ simulations based on the parameters of $ \mathcal{M}^{i} $ , and

- $ S_{b}^{i}\Rightarrow $ simulations based on the logical description of $ \mathcal{L}_{l}^{i} $ System requirements expressed in natural language is the starting point of the RFD process. As a model-based process, it produces two main system models representing the logical and behavioral aspects of the requirements. A simulation is successful if all constraints associated with attributes of the system are met. The objective of behavior model simulation is to describe the operations of a system and the flow of information between the different subsystems. Traditional system simulation can be described as parametric since it focuses on the parameters of a system model. The RFD process introduces formal methods and simulations of system behavior based on the formal logics used to capture the system requirements. There are different levels of system abstraction and refinement in the RFD process. Refinement and abstraction relate inversely to each other. As we go down in the levels (towards the implementation), more granular refinements are obtained.

## B. Formal Requirements Management using Channel Theory

This section presents the formal framework of requirements management for the RFD process based on channel theory. Eqn. 5 illustrates the implementation of the behavioral part of the RFD process $ \mathcal{M}_{B} $ based on channel theory. For simplicity, the superscripts will be omitted.

$$
\mathcal {M} _ {B}: \quad \mathcal {L} _ {n} \iff \overbrace {\mathcal {C} \rightarrow \mathcal {T}} ^ {\mathcal {L} _ {l}} \Downarrow \mathcal {S} _ {b}
$$

where $ \mathcal{C} $ is a classification model (in a table form), $ \mathcal{T} $ is its theory (a set of logical formulas), and $ S_{b} $ is behavioural simulation.

In order to translate the requirements $ \mathcal{L}_{n} $ to a set of logical expressions $ \mathcal{L}_{l} $ , a system should be modeled using a convenient structure in which one can relate logical expressions to it. We use a notion of a classification to model a system, which is formulated from Barwise and Seligman's channel theory. A classification is a model of a system as an informational network (i.e. representing the system using

<!-- PDF_PAGE: 5 -->

the information flow through it), usually presented in a table, see Section II-A. A theory is extracted from a classification. This helps to perform a formal proof for checking consistency (no contradiction) and deducing to a requirement (verifying a property) using a theorem proving approach. In [43], for example, we followed the same approach to ensure consistency in component and system theories of small satellite systems.

Though the logical representation $ \mathcal{L}_{l} $ (strictly, the theory) is used to check correctness of the requirements, it may not fully capture the whole requirements. By mapping the logical representations to behavior simulation, $ S_{b} $ , and comparing to $ \mathcal{L}_{n} $ one can tell whether the requirements are fully captured or not. $ S_{b} $ represents behavior model simulations as state diagrams, activity diagrams [44], [45], Petri nets [46], [47], etc. These graphical tools provide a powerful communication medium between the user, requirements engineer, and the customer [47]. If the behavior simulation $ S_{b} $ associated with $ \mathcal{L}_{l} $ fully captures the requirements of $ \mathcal{L}_{n} $ , then we have equivalence between requirements and its logical representation [2], i.e.

$$
\text {i f} \quad \mathcal {L} _ {l} \quad \text {i s c o n s i s t e n t a n d} \quad \mathcal {S} _ {b} \equiv \mathcal {L} _ {n} \quad \text {t h e n} \quad \mathcal {L} _ {n} \equiv \mathcal {L} _ {l}
$$

On the other hand, if the requirements are not fully captured, we go to the logical representations and make corrections or enhancements.

<div align="center">

Figure 1: The Responsive and Formal Design process

</div>

We assume the same structure (but different level of granularity) for each level of abstraction of the RFD process. As we descend from higher levels of abstraction, we naturally produce more granular refinements. Fig. 1 shows the $ i^{th} $ and $ (i+1)^{th} $ levels of representation with refinement and abstraction relations. Different levels of system abstraction and refinement go hand in hand in an inverse relationship. The refinement relation preserves properties. Abstraction relation is used to trace back to high level requirements. We discussed requirements hierarchy in [48]. In Fig. 1, all parameters are superscripted with the level of abstraction it exists.

## IV. DERIVING A THEORY AND DEDUCTIONS IN A FUZZY CONTEXT

This section presents an algorithm that is used to extract a theory from a fuzzy classification and it is generally based on the algorithm presented in [8] (for a binary case) and follows [18], [22] (for a 'fuzzy' extension).

## A. Extracting a Theory from a Fuzzy Classification

1) Definition:

a) Fuzzy Concepts: Consider a fuzzy classification $ \mathcal{A}=\langle tok(\mathcal{A}),typ(\mathcal{A}),\models_{\mathcal{A}}\rangle $ , L-sets $ \Gamma\in\mathbf{L}^{typ(\mathcal{A})} $ (L-set of types) and $ \Omega\in\mathbf{L}^{tok(\mathcal{A})} $ (L-set of tokens), and $ a\in tok(\mathcal{A}) $ . We define $ \Gamma^{\prime}\in\mathbf{L}^{tok(\mathcal{A})} $ (L-set of tokens) and $ \Omega^{\prime}\in\mathbf{L}^{typ(\mathcal{A})} $ (L-set of types) by modifying Definition 4.1 in [8] and following [16], [19], [20], [22].

- The intended meaning of $ \Gamma^{\prime} $ is "for each $ \alpha\in typ(\mathcal{A}) $ if it is very true that $ \alpha $ belongs to $ \Gamma $ then a realizes $ \alpha $". For a binary classification, a realizes $ \alpha $ if a has $ \alpha $; i.e., $ \models (a,\alpha)=1 $ . "Very true" is interpreted by $ \ast typ(\mathcal{A}) $

$$
\Gamma^ {\prime} (a) = \bigwedge_ {\alpha \in t y p (\mathcal {A})} \Gamma (\alpha) ^ {* t y p (\mathcal {A})} \rightarrow \models_ {\mathcal {A}} (a, \alpha)
$$

- The intended meaning of $ \Omega^{\prime} $ is "for each $ a \in tok(\mathcal{A}) $ : if it is very true that $ a $ belongs to $ \Omega $ then $ a $ has $ \alpha $ ( $ \alpha $ is realized by $ a $ )". "Very true" is interpreted by $ *tok(\mathcal{A}) $ .

$$
\Omega^ {\prime} (\alpha) = \bigwedge_ {a \in t o k (\mathcal {A})} \Omega (a) ^ {* t o k (\mathcal {A})} \rightarrow \models_ {\mathcal {A}} (a, \alpha)
$$

Note that $ \Omega^{\prime} $ is a fuzzy set of types common to all tokens for which it is very true that they belong to $ \Omega $ and $ \Gamma^{\prime} $ is a fuzzy set of tokens sharing all types for which it is very true that they belong to $ \Gamma $ . The set $ \left\{\langle\Omega,\Gamma\rangle\right| \Gamma^{\prime}=\Omega, \Omega^{\prime}=\Gamma \} $ of all points that contains all pairs $ \langle\Omega,\Gamma\rangle $ such that $ \Omega $ is the collection of all tokens that have all the types of "very $ \Gamma $", and $ \Gamma $ is the collection of all types that are shared by all the tokens of "very $ \Omega $" [22]. $ \Omega $ and $ \Gamma $ are called the extent and intent of the concept $ \langle\Omega,\Gamma\rangle $ , respectively.

b) Order: For $ \Gamma\in\mathbf{L}^{typ(\mathcal{A})}, typ(\mathcal{A})=\{1,2,\ldots,n\}, $ $ L=\{0=a_{1}<a_{2}<\ldots<a_{k}=1\},(i,j)\in typ(\mathcal{A})\times L, $ order on $ typ(\mathcal{A})\times L $ is defined as follows [16] and the proofs are also available in the same reference.

Definition 4.1: $(i,j) \leq (r,s)$ iff $i < r$ or $i = r,a_{j} \geq a_{s}$.

Lemma 4.1: $ \Gamma \oplus (i,j):=(\Gamma \cap \{1,2,\dots,i-1\})\cup\{a_{j}/i\}. $

Theorem 4.1: $ \Gamma^{+}=\Gamma \oplus(i,j), $ where $ (i,j) $ is the greatest one with $ \Gamma <_{(i,j)} \Gamma \oplus(i,j). $

c) Uniquely realized types: We then define a set of uniquely realized incompatible types and/or necessity types (called 'strict'incompatible/neccessity types) of a fuzzy classification.

Definition 4.2: For a fuzzy classification $ \mathcal{A} $ $ \Gamma_{strict, \mathcal{A}} $ is a set of 'strict' incompatible/ necessity types of $ \mathcal{A} $ , if $ \forall \Gamma, \Gamma \in \Gamma_{strict, \mathcal{A}} $

- For each $ a\in tok(\mathcal{A}),\exists !\alpha\in typ(\mathcal{A}) $ such that it is very true that $ \alpha $ belongs to $ \Gamma. $

- A degree of strictness can be defined; however, in this paper, we use a degree of 1.

<!-- PDF_PAGE: 6 -->

2) Extracting Entailment Formulas: A theory of a classification $ \mathcal{A} $ consists of three main kinds of constraints. For $ \Lambda, \Gamma, \Delta\in\mathbf{L}^{typ(\mathcal{A})}, $

$ T_{1}. $ Incompatible types: The intended meaning is there is no token of the classification $ \mathcal{A} $ that is of all types in $ \Gamma. $

- If $ \Lambda\in\Gamma_{strict,\mathcal{A}} $ and for $ \alpha\in typ(\mathcal{A}),card(\alpha|\Lambda(\alpha)\neq 0) > 1,\Lambda\vdash\emptyset $ ; where $ card(\cdot) $ is cardinality. A single type can not be incompatible with itself.

$ T_{2}. $ Necessity: The meaning is every token of the classification is of some type in $ \Delta. $

- If $ \Lambda\in\Gamma_{strict,\mathcal{A}},\emptyset\vdash\Lambda. $

$ T_{3}. $ Entailment: The meaning is if each token having all types from $ \Gamma $ has some types from $ \Delta. $

- These constraints are extracted from the intent $Int(\cdot)$ of the fuzzy concept. Different algorithms (e.g., [16]) can be used to extract such a set. For $ \Lambda\in Int(\mathcal{A}),\langle\Gamma,\Delta\rangle $ a partition of $ \Lambda $ , and $ \| \Gamma\vdash\Delta\|_{\mathcal{A}}=1 $ , then $ \Gamma\vdash\Delta. $

We developed Algorithm IV.1 to extract such constraints from a fuzzy classification.

Algorithm IV.1 Theory Extraction

1: INPUT: $ \mathcal{A} $ ▷ Fuzzy classification

2: Compute $ \Gamma_{strict},\mathcal{A} $ and $ Int(\mathcal{A}) $

3: for $ \Lambda \in \mathbf{L}^{typ(\mathcal{A})} $ do

4: if $ \Lambda \in \Gamma_{strict},\mathcal{A} $ then

5: $ \emptyset \vdash \Lambda \in T_{2} $

6: if $ card(\alpha|\Lambda(\alpha) \neq 0)_{\alpha \in typ(\mathcal{A})} > 1 $ then

7: $ \Lambda \vdash \emptyset \in T_{1} $

8: end if

9: else if $ \Lambda \in Int(\mathcal{A}) $ then

10: Compute partitions of $ \Lambda $

11: for $ \langle \Gamma, \Delta \rangle \in Partitions(\Lambda) $ do

12: if $ \| \Gamma \vdash \Delta \|_{\mathcal{A}} = 1 $ then

13: $ \Gamma \vdash \Delta \in T_{3} $

14: end if

15: end for

16: end if

17: $ \Lambda := \Lambda^{+} $

18: end for

19: $ Th(\mathcal{A}) = T_{1} \cup T_{2} \cup T_{3} $

20: OUTPUT: $ Th(\mathcal{A}) $ ▷ Theory

## B. Deducing a Requirement and Ensuring Consistency

A given requirement (represented as a sequent) is consistent with the system if we can derive (prove) it from a theory. A derivation or proof within this theory is as usual a sequence of sequents, where each of the sequents in the sequence is either a premise (element of the theory) or is deduced from previous sequents appearing in the sequence using one of deduction (Armstrong-like) rules from [6] (cf. [9], [14], [49] for implication, see [17], [22] for fuzzy form) described as:

(Ide) infer $ \Gamma\vdash\Gamma, $

(Wea) from $ \Gamma \vdash \Delta $infer $ \Gamma \cap \Gamma^{\prime}\vdash \Gamma \cup \Delta^{\prime}, $

(Cut) from $ \Gamma\cap\Sigma_{0}\vdash\Delta\cup\Sigma_{1} $ for each partition $ \langle\Sigma_{0},\Sigma_{1}\rangle $ of $ \Sigma^{\prime} $ infer $ \Gamma\vdash\Delta, $ (Tra) from $ \Gamma\vdash\Delta $ and $ \Delta\vdash\Sigma $ infer $ \Gamma\vdash\Sigma, $

(Mul) from $ \Gamma\vdash\Delta $ infer $ c^{*} \otimes\Gamma\vdash c^{*} \otimes\Delta. $ for each $ \Gamma, \Delta, \Sigma, \Sigma^{\prime}\in L $ , and $ c\in L. $

A theory should satisfy these rules for all sets $ \Gamma, \Gamma^{\prime}, \Delta, \Delta^{\prime}, \Sigma^{\prime}, \Sigma_{0}, \Sigma_{1} $ of types and is called regular.

A fuzzy type formula $ \Gamma\vdash\Delta $ is called provable from a set T of fuzzy type formula, theory, using deduction rules, written as $ T\vdash\{\Gamma\vdash\Delta\} $ (cf. [17]). If "from $ \psi_{1},\dots,\psi_{n} $ infer $ \psi $ " is a rule derivable from the ordinary Armstrong axioms [9], [14], [49] then replacing symbols of sets by symbols of fuzzy sets, the rule is derivable from the above rules.

Similar to implication provability [17], [22], we can define the degree in which a requirement is deduced from a theory. In this paper, we only consider degree of 1 for provability (see [17], [21], [22] for graded provability and entailment).

## V. EXAMPLE

We will consider auroral imaging example taken from [43]. Understanding the impact of the solar wind on the Earth and near-Earth space is of growing importance in our technology dependent society. This can be done by studying auroral ovals, which are optical manifestations of the large-scale electric currents that flow upward and downward along the terrestrial magnetic field lines. They help us elucidate the physics of magnetosphere-ionosphere coupling, which is essential to improving our space weather prediction capabilities.

Consider a system of three small satellites, $ S_{1}, S_{2} $ and $ S_{3} $ , whose goal is to image the auroral ovals that exist around both magnetic poles of Earth and thereby study the impact of the solar wind on the magnetosphere. $ S_{1} $ measures the intensity of the auroral brightness; if this is over a given threshold, then $ S_{1} $ measures the magnetic disturbance density and sends a message to $ S_{2} $ and $ S_{3} $ to begin imaging. $ S_{2} $ and $ S_{3} $ do the same thing from different perspectives, viz., take an image of the auroral oval to determine its extent.

In this paper, however, we differ in two ways. The first is the way we define the situation features (types) and classify the situations (tokens); and the second is we use a fuzzy relation between tokens and types (instead of a binary relation).

We classify the small satellite measurement system based on what the satellites are doing. The system is modelled using a classification structure. We classify the first satellite at times $ s_{1,t} $ , for example, based on what it is doing, resulting in three types - LAB (measuring Low Auroral Brightness), HAB (measuring High Auroral Brightness), MDD (measuring Magnetic Disturbance Density), Tx (transmitting or transmitter is on), and REV1 $ (S_{1} $ is revolving or motor is working). $ s_{1,t}\models \mathrm{LAB} $ if $ S_{1} $ measures low auroral brightness around Earth's magnetic poles. Of course, classifying the tokens using types has its own uncertainty. The classification is shown in Table I.

The remaining component classifications are defined in a similar way.

<!-- PDF_PAGE: 7 -->

<div align="center">

Table I: Classification $ S_{1} $

</div>

<table border="1"><tr><td>$ \models_{S_{1}} $</td><td>LAB</td><td>HAB</td><td>MDD</td><td>Tx</td><td>REV1</td></tr><tr><td>$ a_{1} $ low auroral brightness</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$ a_{2} $ high auroral brightness</td><td>0</td><td>1</td><td>0.5</td><td>0</td><td>1</td></tr><tr><td>$ a_{3} $ transmitting</td><td>0</td><td>1</td><td>1</td><td>0.5</td><td>1</td></tr></table>

- The second satellite classification, $ S_{2}=\langle tok(S_{2}),typ(S_{2}),\models_{S_{2}}\rangle $ : There are many ways to classify the satellite. The tokens of $ S_{2} $ consist of status of the second satellite at various times. Types are Rx2 (the second satellite is receiving or receiver of the second satellite is on), TP2 $ (S_{2} $ is taking pictures), and REV2 (revolving).

- The third satellite classification, $ S_{3}=\langle tok(S_{3}),typ(S_{3}), $ $ \models_{S_{3}} $ ): Similarly, the tokens of $ S_{3} $ consist of the status of the third satellite at various times. Types are Rx3 (the third satellite is receiving or receiver of the third satellite is on), TP3 $ (S_{3} $ is taking pictures), and REV2 (revolving).

Table II shows the remaining component classifications.

<div align="center">

Table II: Component classifications

</div>

<div align="center">

(a) Classification $ S_{2} $

</div>

<div align="center">

(b) Classification $ S_{3} $

</div>

<table border="1"><tr><td>$=S_{2}$</td><td>Rx2</td><td>TP2</td><td>REV2</td></tr><tr><td>$b_{1}$ waiting</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$b_{2}$ taking picture</td><td>0.5</td><td>1</td><td>1</td></tr><tr><td>$c_{1}$ waiting</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$c_{2}$ taking picture</td><td>1</td><td>1</td><td>1</td></tr></table>

The core classification $ S $ (that represents the whole system) is the categorical sum (see Definition 2.6) of the component classifications $ S_{1}, S_{2} $ , and $ S_{3} $ . The types and tokens of the sum of classifications is defined as the disjoint union and cartesian product of the types and tokens of the component classifications respectively. The sum $ S=S_{1}+S_{2}+S_{3} $ is the classification defined as:

1) The set $tok(\mathcal{S}_1 + \mathcal{S}_2 + \mathcal{S}_3)$ of tokens is the cartesian product of $tok(\mathcal{S}_1),tok(\mathcal{S}_2)$, and $tok(\mathcal{S}_3)$. This maps the local properties of the components to global properties of the whole system.

2) The set $ typ(\mathcal{S}_{1}+\mathcal{S}_{2}+\mathcal{S}_{3}) $ of types is the disjoint union of $ typ(\mathcal{S}_{1}), typ(\mathcal{S}_{2}), $ and $ typ(\mathcal{S}_{3}). $

3) The classification relation $ \models_{\mathcal{S}_1+\mathcal{S}_2+\mathcal{S}_3} $ of $ \mathcal{S}_1+\mathcal{S}_2+\mathcal{S}_3 $ is defined by $ (a_{1},a_{2},a_{3})\models_{\mathcal{S}_{1}+\mathcal{S}_{2}+\mathcal{S}_{3}}\langle i,\alpha\rangle $ only if $ a_{i}\models_{\mathcal{S}_{i}} $ $ \alpha, \forall i\in\{1,2,3\}. $

The core classification is shown in Table III.

<div align="center">

Table III: Core classification $ \mathcal{S} $

</div>

<table border="1"><tr><td rowspan="2">$ \models_{S} $</td><td colspan="5">$ S_{1} $</td><td colspan="3">$ S_{2} $</td><td colspan="3">$ S_{3} $</td></tr><tr><td>LAB</td><td>HAB</td><td>MDD</td><td>Tx</td><td>REV1</td><td>Rx2</td><td>TP2</td><td>REV2</td><td>Rx3</td><td>TP3</td><td>REV3</td></tr><tr><td>$ d_{1} $</td><td>1</td><td>0</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$ d_{2} $</td><td>0</td><td>1</td><td>0.5</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$ d_{3} $</td><td>0</td><td>1</td><td>1</td><td>0.5</td><td>1</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$ d_{4} $</td><td>0</td><td>1</td><td>1</td><td>0.5</td><td>1</td><td>0.5</td><td>1</td><td>1</td><td>0</td><td>0</td><td>1</td></tr><tr><td>$ d_{5} $</td><td>0</td><td>1</td><td>1</td><td>0.5</td><td>1</td><td>0</td><td>0</td><td>1</td><td>1</td><td>1</td><td>1</td></tr></table>

$ d_{1}=\langle a_{1}, b_{1}, c_{1}\rangle $ : low auroral brightness; $ d_{2}=\langle a_{2}, b_{1}, c_{1}\rangle $ : high auroral brightness;

$ d_{3}=\langle a_{3}, b_{1}, c_{1}\rangle $ : transmitting; $ d_{4}=\langle a_{3}, b_{2}, c_{1}\rangle $ : $ S_{2} $ is taking pictures; and

$ d_{5}=\langle a_{3}, b_{1}, c_{2}\rangle $ : $ S_{3} $ is taking pictures.

Consider the following fuzzy consequence relation formulas from the core classification.

1) $ \{^{0. 5} /_{\mathrm{T x}} \} \vdash \{ \mathrm{REV1}, \mathrm{REV2}, \mathrm{REV3} \} $ is a fuzzy consequence relation formula which is true in degree 1.

2) {HAB, REV1} $ \vdash $ $ \{^{0.5} /_{\mathrm{MDD}} \}$ is true in degree 1. But, {HAB, REV1} $ \vdash $ {MDD} is not true in degree 1; token $ d_{2} $ is a counterexample.

3) $ \emptyset \vdash \{ \mathrm{L A B}, \mathrm{H A B} \} $ is a crisp and it is true in degree 1. Table IV presents the theory of the core classification.

<div align="center">

Table IV: Theory of the core classification

</div>

<table border="1"><tr><td>$Th(S)=Th(S_{1}+S_{2}+S_{3})$</td></tr><tr><td>$r_{1}: \{ \mathrm{LAB}, \mathrm{HAB}\} \vdash \emptyset$</td></tr><tr><td>$r_{2,3,4,5}: \emptyset \vdash \{ \mathrm{LAB}, \mathrm{HAB}\}; \emptyset \vdash \{ \mathrm{REV1}\}; \emptyset \vdash \{ \mathrm{REV2}\}; \emptyset \vdash \{ \mathrm{REV3}\}$</td></tr><tr><td>$r_{6,7,8}: \{ \mathrm{HAB}\} \vdash \{ ^{0.5}_{/ \mathrm{MDD}}\}; \{ ^{0.5}_{/ \mathrm{MDD}}\} \vdash \{ \mathrm{HAB}\}; \{ \mathrm{HAB}, ^{0.5}_{/ \mathrm{Tx}}\} \vdash \{ ^{0.5}_{/ \mathrm{MDD}}\}$</td></tr><tr><td>$r_{9,10}: \{ \mathrm{HAB}, ^{0.5}_{/ \mathrm{Tx}}, ^{0.5}_{/ \mathrm{Rx2}}\} \vdash \{ \mathrm{TP2}\}; \{ \mathrm{HAB}, ^{0.5}_{/ \mathrm{Tx}}, \mathrm{Rx3}\} \vdash \{ \mathrm{TP3}\}$</td></tr></table>

A requirement of the system is expressed by the constraint

$$
r: \left\{\mathrm {H A B}, ^ {0. 5} / _ {\mathrm {T x}}, ^ {0. 5} / _ {\mathrm {R x 2}}, \mathrm {R x 3} \right\} \vdash \left\{\mathrm {T P 2}, \mathrm {T P 3} \right\}
$$

that reads as "it is likely that the two satellites will take images of the auroral ovals from different perspectives if the third satellite measures high auroral brightness and sends messages to them". It is proved that this constraint is derivable from $ Th(\mathcal{S}) $ as:

Proof 5.1: Deriving a requirement $r$ from a theory $Th(S)$

1. $ \{ \mathrm{H A B},^{0. 5} / _ {\mathrm{T x}},^{0. 5} / _ {\mathrm{R x 2}} \} \vdash \{ \mathrm{T P 2} \}$ Given rule, $r_{9}.$

2. $ \{ \mathrm{H A B},^{0. 5} / _ {\mathrm{T x}},\mathrm{R x 3} \} \vdash \{ \mathrm{T P 3} \}$ Given rule, $r_{10}.$

3. $ \{ \mathrm{H A B},^{0. 5} / _ {\mathrm{T x}},^{0. 5} / _ {\mathrm{R x 2}},\mathrm{R x 3} \} \vdash \{ \mathrm{T P 2},\mathrm{H A B},^{0. 5} / _ {\mathrm{T x}},\mathrm{R x 3} \} $Wea rule on 1.

4. $ \{ \mathrm{H A B},^{0. 5} / _ {\mathrm{T x}},^{0. 5} / _ {\mathrm{R x 2}},\mathrm{R x 3} \} \vdash \{ \mathrm{T P 2},\mathrm{T P 3} \}$ Tra rule, 3, 2.

## VI. CONCLUSION

This paper uses a fuzzy relation as a system model to be used for the RFD process, which relates a set of requirements, associated models, simulations, and the relationship between them, by integrating Model-Based System Engineering with formal methods. We used the notion of a classification (presented using a table) to model (components and) a system which is formulated from Barwise and Seligman's channel theory. This helps us to link our specification to logical expressions from which a formal proof is possible. However, modeling a distributed system using a classification (and a theory) based on a binary relation (using 0s and 1s) between tokens and types (as it is used in channel theory) is not always possible, since it involves vagueness and imprecision. The representation lacks expressiveness to reason about relations among such types (vague situation features). In this paper, we defined a fuzzy classification to improve this limitation. We showed how to extract a theory from a fuzzy classification. We also showed how to define and achieve consistency in a fuzzy classification context. We demonstrated our development using three small satellites measurement system whose goal is to image the colorful auroral ovals seen around Earth's magnetic poles.

## REFERENCES

<!-- PDF_PAGE: 8 -->

[2] W. Edmonson, J. Chenou , N. Neogi, and H. Herencia-Zapana, "Small satellite systems design methodology: A formal and agile design process," $ 8^{th} $ Annual IEEE International Systems Conference, pp. 518-524, 2014.

[3] "INCOSE systems engineering vision 2020," 2007. [Online]. Available: http://www.incose.org/ProductsPubs/products/sevision2020.aspx.

[4] J. Wing, "A specifiers introduction to formal methods," IEEE Computer, vol. 23, no. 9, p. 824, 1990.

[5] J. Barwise and J. Seligman, "Imperfect information flow," Proceedings of Eighth Annual IEEE Symposium on Logic in Computer Science, pp. 252-260, June 1993.

[6] J. Barwise and J. Seligman, Information Flow The logic of Distributed Systems. Cambridge Tracks in Theoretical Computer Science, 1997.

[7] L. Zadeh, "Fuzzy sets," Information and Control, pp. 338-353, 1965.

[8] S. Gebreyohannes, W. Edmonson, J. Chenou, N. Neogi, and A. Esterline, "Formal requirement management for the Responsive and Formal Design Process," First IEEE International Symposium on Systems Engineering, September 2015.

[9] W. W. Armstrong, "Dependency structures in data base relationships," IFIP Congress, Geneva, Switzerland, pp. 580-583, 1974.

[10] B. Ganter, "Two basic algorithms in concept analysis," ICFCA'10, Springer-Verlag Berlin, Heidelberg, pp. 312 - 340, reprint 2010.

[11] Y. Zhai, D. Li, K. Qu, "Decision implication canonical basis: A logical perspective," Journal of Computer and System Sciences 81, pp. 208- 218, 2014.

[12] H. Shi, Q. Hua and B. Zhang, "The canonical basis of implicational system," International Conference on Machine Learning and Cybernetics, pp. 1076 - 1081, 2006.

[13] Z. Xie and Z. Liu, "From intent reducts for attribute implications to approximate intent reducts for association rules," International Conference on Computer and Information Technology, pp. 162 - 169, 2005.

[14] D. Maier, "The theory of relational databases," Computer Science Press, Rockville, 1983.

[15] T. Furukawa and F. Sha, "Utilizing functional dependencies in multidimensional databases," International on Symposium on Applications in Non-Traditional Environments, pp. 59-65, 1999.

[16] R. Belohlavek, "Algorithms for fuzzy concept lattices," in Proc. Fourth Int. Conf. on Recent Advances in Soft Computing. Nottingham, United Kingdom, 2002, pp. 200-205.

[17] R. Belohlavek and V. Vychodil, "Axiomatizations of fuzzy attribute logic." in IICAI, vol. 5, 2005, pp. 2178-2193.

[18] R. Bělohlávek and V. Vychodil, "Implications from data with fuzzy attributes vs. scaled binary attributes," in Fuzzy Systems, 2005. FUZZ'05. The 14th IEEE International Conference on. IEEE, 2005, pp. 1050- 1055.

[19] R. Belohlavek, T. Funiokova, and V. Vychodil, "Galois connections with hedges," IFSA Congress, 2005.

[20] R. Belohlavek and V. Vychodil, "Reducing the size of fuzzy concept lattices by hedges," FUZZ-IEEE, The IEEE International Conference on Fuzzy Systems, pp. 663-668, May 2005.

[21] R. Belohlavek and V. Vychodil, "Fuzzy attriute logic: syntactic entailment and completeness," JCIS, $ 8^{th} $ Joint Conference on Information Sciences, Utah, USA, pp. 78-81, July 2005.

[22] R. Bělohlávek and V. Vychodil, "Attribute implications in a fuzzy setting," in Formal Concept Analysis. Springer, 2006, pp. 45-60.

[23] M. Baczynski and B. Jayaram, "Fuzzy implications," Springer-Verlag Berlin, Heidelberg, 2008.

[24] Y. Shi, "A deep study of fuzzy implications," PhD Dissertation, Ghent University, 2009.

[25] V. Vychodil, "Fuzzy attribute implications and their expressive power," International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems, vol. 21, no. 4, pp. 483-496, 2013.

[26] M. Nakata, "Dependencies in fuzzy databases: Functional dependency," IEEE International Conference on Fuzzy Systems and International Fuzzy Engineering Symposium, vol. 2, pp. 757-764, 1995.

[27] K. Bharath, "The logic of information flow: A graded approach," Thesis, Binghamton University, NY, 2008.

[28] R. Yager (ed.), Fuzzy Set and Possibility Theory. New York, Oxford, Toronto: Pergamon Press, 1982.

[29] G. Klir and B. Yuan, Fuzzy Sets and Fuzzy Logic Theory and Applications. Prentice Hall, 1995.

[30] G. Klir, U. Clair, and B. Yuan, Fuzzy set theory: foundations and applications. Prentice Hall, 1997.

[31] Li-Xin Wang, A course in Fuzzy Systems and Control. Prentice-Hall, 1997.

[32] R. Yager and L. Zadeh, An Introduction to Fuzzy Logic Applications in Intelligent Systems. Norwell, MA: Kluwer Academic Publisher, 1992.

[33] R. Belohlavek, Fuzzy Relational Systems: Foundations and Principles. New York: Kluwer, Academic/Plenum, 2002.

[34] H. Zimmermann, Fuzzy Set Theory and its Applications, $ 4^{th} $ ed. New York: Springer Science+Business Media, 2001.

[35] T. J. Ross, Fuzzy Logic with Engineering Applications, $ 2^{nd} $ ed. England: John Wiley & Sons Ltd, 2004.

[36] W. Pedryex and F. Gomide, "An introduction to fuzzy sets: Analysis and design," 1998.

[37] M. Dhar, "A note on subsethood measure of fuzzy sets," IJEIC, vol. 3, no. 3, 2012.

[38] J. Wertz and W. Larson, Space Mission Analysis and Design. Microcosm Press, 1999.

[39] W. Edmonson, S. Gebreyohannes, A. Dillion, R. Radhakrishnan, J. Chenou, A. Esterline, and F. Afghah, "Systems engineering of intersatellite communications for distributed systems of small satellites," 9th Annual IEEE International Systems Conference (SysCon), pp. 705-710, April 2015.

[40] J. Rasmussen, "A framework for cognitive task analysis in systems design," Riso National Laboratory, Denmark, 1985.

[41] T. Yagiu, "A categorical model of design process (rev. 1)," WS on Design and Functions, July 2001.

[42] K. Minamizono, O. Katai, T. Shiose, and H. Kawakami, "Analyses of design processes based on category theory and channel theory," SICE Annual Conference in Fukui, vol. 1, pp. 961-966, August 2003.

[43] J. Chenou, W. Edmonson, A. Esterline and N. Neogi, "Formal framework for ensuring consistent system and component theories in the design of small satellite systems," Complex Systems and Data Management Conference, 2014.

[44] S. Friedenthal, A. Moore, and R. Steiner, A Practical Guide to SysML: The Systems Modeling Language. Burlington: MA: Morgan Kaufman Publishers, 2009.

[45] L. Delligatty, SysML Distilled - A Brief Guide To The Systems Modeling Language. Pearson Education, Inc, 2014.

[46] T. Murata, "Petri nets: Properties, analysis and applications," Proc. Of the IEEE, vol. 77, no. 4, pp. 541 - 580, 1989.

[47] R. Zurawski and M. Zhou, "Petri nets and industrial applications: A tutorial," IEEE Transactions on Industrial Electronics, vol. 41, no. 6, pp. 567 - 583, 1994.

[48] S. Gebreyohannes, W. Edmonson, A. Esterline, and J. Chenou, "Requirement hierarchy for the Responsive and Formal Design Process," Second IEEE International Symposium on Systems Engineering, December 2016.

[49] C. Beeri, M. Dowd, R. Fagin, R. Statman, "On the structure of armstrong relations for functional dependencies," Journal of the ACM, 1984.