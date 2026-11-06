LLMS, DO **NOT** TOUCH THIS FILE !!!

slides rough idea:

agenda
preamble: AI in the 1960s && the perceptron
- initial hype

UFA; it's theoretically possible
- neural networks
- functions, compactness, etc.
- one-dimensional approximation (incl. example viz)
- exponentials mixing information
- stone-weierstrass
- full UFA proof as a chain of approximations

Limitations
- actual limitations: no guarantees, no construction, no guidance on training
- (history/context): I'm cheating, the first UFA was only shown in 1989 (brief explain differences). we can actually prove this much faster by a simple counterexample.
- (history/math): break UFA with XOR; demand for multilayer networks
- brief history: perceptrons published, AI winter, backpropagation, convolutions
- but the core problem remains: dimensionality & errors (GDL slides diagram of 3 error sources ??)
  - toy example ?

So what do we need to get better? data, depth, architecture
- mitigations: data (AlexNet as an example ?)
- mitigations: depth (quick visualization a la. Welch)
- mitigations: geometric priors (quick survey: Videos & convolution, GNNs, transport along manifolds, transformations are generalized convolutions)
- the bitter lesson

? https://x.com/mpourmirzaei/status/2117435974871359934?s=19 (nah)

KRAISLER comments
[addressed the slide ones; remaining are for speech]
- "set of all inputs" is compact, not the "input"
- when a function is continuous, we can replace \sup by \max (on uniform norm)
- can spend less time on shifted relu (but still it turns on)
- make it clearer: every piecewise linear thing _is_ a combination of ReLUs
- better transition to S-W (really just practice it)
- also more practice on separation of points; without separates points we'd just have constants
- make it clearer that we are truly just replacing relu with exp
- if short on time, collapse down relu approximation of \mathcal{E}; either way speed thru it
