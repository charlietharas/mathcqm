This is really a talk about AI

The story of AI starts a long time ago--as early as the mid 19th century, Samuel Butler's Erewohn warned of a world with "no security against the ultimate development of technical consciousness." In 1847, Cauchy invented gradient descent (my favorite algorithm of all time), which is at the heart of countless digital systems and fundamental to the modern theory of machine learning. And of course, there are examples earlier than that. In 1950, Alan Turing, the father of computer science, proposed his infamous "Imitation Game", or Turing Test.

But our story starts just a few years after that, in 1958, with Frank Rosenblatt's perceptron. This was a complex machine, built on a simple algorithm which could learn by itself to linearly separate multi-dimensional data. We'll learn how his perceptron works today. 
Publicity <quote>
In fact at that time people were convinced that what we might call "AGI" was right around the corner.
In 1966 MIT launched a Summer Vision Project to construct "a significant part of a visual system."
<more quotes ??>

Sadly this optimism was not to last. In 1969 Miarvin Minsky and Seymour Papert, the man who led that project, published "Perceptrons," which ironically is foundational to today's theory of deep learning. Ironic bc it completely killed the field, demonstrating that current methods failed to compute solutions to a broad class of problems and lacked any guidance on how to actually train and build these networks.

So the field languished for over a decade, until in the late 1980s a wave of results shook the world of computer science. We discovered backpropagation, a generalized algorithm that enables deeper neural networks to learn.
Yann LeCun, up until recently the chief of AI at Meta, built a real-world neural network that accurately read the zip codes off of envelopes.
And George Cybenko was the first of money to prove a set of results on universal function approximation, which is what we'll be discussing today.

<UFA states: >

But what is a neural network?
- function
- d dimensional input
- single output in R
- theta parametrizes

Neurons
- take in some input x
- 'computational bulk' is the affine function (weights, bias)
- but the key to their so-called intelligence is nonlinearity
<prevents collapse>
in particular, relu
others used because of differences in how they caused neural networks to train, some exhibit better performance on specific tasks. relu or close variants however are popular today because they are simple and they work.
we use them as the nonlinearity applied to every neuron, hence we call it "ReLU networks"

Now, with all our neurons, how do we combine them together? Where does the network part come in?
- essentially just another neuron over all the neurons
  ( denoted h_j)

The nonlinearities let us stack layers
- note how we can write each one as a matrix multiplication
- this is why all the GPUs are gone

But in our case we only care about single hidden layer, and will mostly stay away from/not be concerned with vectors. You're welcome.

(spoke to soon) <inputs & target>
- we restrict our inputs to [0, 1] for simplicity (helps with some of the notation & algebra)
- but the important point is it is compact, our results generalize to all compact domains
- we need compactness to apply restrictions to its outputs, you'll see what i mean in a second

recall: <heine-borel>

we need this for <uniform continuity>
- recall ordinary continuity lets the output bound depend on the input coordinate, uniform does not (hence uniform)

<function classes... uniform norm>

how are we going to use all of these?
- uniform continuity gives bounds, anywhere on the function
- ...

okay! we'll get started in one dimension, as a warmup. this result will also be useful later in our full proof.
- <one dimensional approx ...>

this was a perfectly good piecewise function that we just built, but we need to write this as a ReLU neural network.
- remember our friend relu?
- notice what happens if we shift its input down
- this behavior acts as a kind of "gate" that only turns on a neuron past a certain input. again, this is a key part of the "intelligence" here! if we stack a bunch of these things, we can get some pretty complex behavior

case in point: <correcting the slope>
- so, we can build a continuous piecewise function exactly with a neural network

but... this was only over one dimension
this gets trickier with additional dimensions. in one dimension, we can use a point to bifurcate the entire interval. but in two or more dimensions, a point no longer constitutes a boundary. so we can't cleanly "turn on and off" in the same way.

we need more. we understand very well how to split one dimension in half--so how can we use that? well, we need to mix the information from both dimensions. 
- how can we combine them? 
- let's try addition <nope>
- how about multiplication

so multiplication works. but how can we describe a neuron as a multiplication of other neurons?
- well we can't right now
- but, we _could_ if we just made them exponential instead. let's swap out our nonlinearity for exponentials!

why would we do this?
- for mathematical reasons. we get save ourselves a lot of work and apply a really powerful theorem that guarantees approximation straightaway
- then once we have an exponential network which we know can approximate any continuous function, we can approximate that network, and as long as we're within bounds, it technically counts!
- nobody _actually_ builds networks like this, they would spit on u if you proposed it (feisty)
- but this is just the first of many reasons why this result is utterly useless. more on that soon! first, some math

<stone-weierstrass>
- suppose we have (as discussed) our compact domain, and some set of functions that we can create with certain building blocks
- these building blocks give us the tools to do approximation. essentially, we're saying that any set of functions with this language, this expressivity, can describe all continuous functions on a compact domain
- we won't be proving this today, someone else did all the hard work. it's essentially a short checklist to see if we have the required capabilities
- [hypotheses](in particular distinguish points)

<apply s-w>
- linear combinations of linear combinations are linear combination

now as promised, and as we did before, we're going to need to convert this back to a ReLU network. luckily this part is really easy! we can just apply our one-dimensional approximation result from before
- notice <ReLU approximation>
- we can define some new error tolerance eta
- taking care to make sure we are respecting compactness, we just approximate each exponential neuron with an exponential network
- then if we combine all of those networks (in parallel), and weight their outputs accordingly, we still have a single-layer network
- now, we need to choose our error tolerance eta carefully. remember that in these terms we have this a_j factor (the output weight for that neuron) which we need to account for
- but if we account for that with this somewhat unweildy expression, we can get the final error tolerance of our approximation of the exponential network down to eps/2

so, if we combine the exponential network and its approximation, our total error tolerance is under budget, and we get our desired result.

this is super cool! what does it get us
- well, not: <limitations>

arguably the biggest problem of the many i just mentioned is that we have no information about how to build the real network
- in the real world <learn from samples>

so we're in a tricky situation where we have infinite possible answers, and no real way to get to a solution. where do we go from here? what can we ask?
- well, how good is our approximation--the one we do have?
- can we get to a halfway decent approximation when we actually train this network on our data?
- what happens if we try to feed it data it hasn't seen before?

this might be a little unintuitive, but i really want you to try to visualize this problem.
on this loose diagram, imagine we have sort of a space of all possible functions. f* here is our true, actual function.
- remember in the real world we tend to have absolutely no idea what f* might be (or if it even _really_ exists!)
- there's a set of all possible functions we can build with our neural network. if we change its size, or its neurons, or add more layers (we'll get to that in a minute), we can maybe move this around
- but in fact our network only learns from data. so there's actually a different set of possible functions _any_ network could learn given all the possible data! that's in pink here.
- this point in pink is the best possible network we can learn given the data [more-to-say]
- but actually, even within our possible networks, we might be training really badly! we might be nowhere near the data, let alone the ground truth. our optimization might suck, we might not have enough compute, we might be totally lost.

so in practice, it is so hard to get all of these sources of error under control. and it actually gets even worse when our data is more complex--when it has higher dimensions
- remember how we had to mix information from different coordinates to sort of split our space up into sections where our neurons can turn on and off?
- well, the more dimensions we have, the more information we need to mix
- a lot more. *exponentially more*
- this is the curse of dimensionality

there is lots more to say about this.
a skeptic among you might say okay, well, three dimensions seems like plenty. we live in three dimensions! and so what if we need more; we have super fast computers!
well, for a large language model, which predicts one of around a hundred thousand output tokens, we need a hundred thousand dimensions. for a reasonably sized image, we need millions.

so how do we get around this?
<sama joke>
<rlvr explanation>

in addition, we can use multilayer networks. multilayer networks make it massively more efficient to operate over the structure of underlying data. there's a lot more to say about this, [welch-labs], but for now just enjoy this pretty visualization <brief explanation>

perhaps the most important approach, though, is to design networks that can leverage the structure of the data they work on.
there is a sort of axiomatic hypothesis within the machine learning/statistics communities that says that we expect that our data, however complex and high-dimensional, is created by relatively simple processes, and thus lies on some relatively low-dimensional manifold within our sampled data.
this is the "manifold hypothesis", and if we assume it is true, we can get a lot of mileage out of our data

i'll borrow one particular way of framing this from some folks who are both brilliant and arrogant enough to call themselves the New Erlangen Programme, after the old one at FAU led by Felix Klein which gave birth to the modern mathematical study of geometry
these folks practice what they call Geometric Deep Learning, and the basic ethos is that, much like in theoretical physics, we must respect the symmetries of our data
for instance, <CNNs / GNNs>

the geometric deep learning blueprint, and building specialized architectures that respect the structure of the world they try to model, can be very powerful in rendering certain classes of problems tractable.
but if there's one thing i want you to take away from this talk, it's an unfortunate observation that you might find hard to swallow, one that Richard Sutton (from backprop earlier) calls "The Bitter Lesson"
<bitter lesson>

<closing>