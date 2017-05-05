# an ultra-complex math library
A hardcore math library with many features - regarding 'ultra-complex' math - you'll never find anywhere else. Don't get me wrong - the images you see won't blow your mind - it's more like that these things even can be computed by a library.

## Topic
It started with the three base types of hyper-complex numbers.
- complex (imaginary times itself equals -1)
- binary (imaginary times itself equals 1 - but isn't 1 itself)
- dual (imaginary times itself equals 0 - but isn't 0 itself)

But eventually it was about all it's combinations, too. A single number then has 8 dimensions - each one corresponding with all other dimensions in a unique way. Then I implemented pretty much all mathematical operations for them - which is anything other than trivial by the way. But right there it'll get too complex, better just look at these first pictures:

### Color mappings

![mapper_comp](https://cloud.githubusercontent.com/assets/23620495/25764400/db0726cc-31e7-11e7-86d8-55675637c858.png)

Color mapping of simple complex cosine


![mapper_bin](https://cloud.githubusercontent.com/assets/23620495/25764403/dc9d678a-31e7-11e7-94ac-692c5ad722ad.png)

Color mapping of simple binary cosine


![mapper_dual](https://cloud.githubusercontent.com/assets/23620495/25764404/deb80c78-31e7-11e7-8a1f-59aea3e7124f.png)

Color mapping of simple dual cosine


And then there's a function plotter showing different dimensions of an 8-dimensional function that shows basically the eulerian behaviour of each base-algebra.

![plotter](https://cloud.githubusercontent.com/assets/23620495/25764397/d9cab5e4-31e7-11e7-8b31-4bb641dc13f1.png)

plotter showing an eight-dimensional function


### Eulerian behaviour

![euler_complex](https://cloud.githubusercontent.com/assets/23620495/25764838/05ead8be-31ea-11e7-917f-f2db49bce0ee.png)

the well-known and loved complex e^(x × π × î) - round

![euler_binary](https://cloud.githubusercontent.com/assets/23620495/25764839/07710c76-31ea-11e7-9444-3f39d9a45ab1.png)

the not so well-known binary e^(x × π × Ê) - hyperbolic

![euler_dual](https://cloud.githubusercontent.com/assets/23620495/25764842/089336b0-31ea-11e7-8693-2c61199101b9.png)

and the not so spectacular dual e^(x × π × ê) - vertical

### Supported operations

- all basic operations (+, -, *, /)
- all trigonometric operations (cos, acos, cosh, acosh, sin, asin, sinh, asinh, tan, atan, tanh, atanh, cot, acot, coth, acoth, sec, asec, sech, asech, csc, acsc, csch, acsch)
- pow, exp, ln, log
- sqrt, conjugate, inverse, re, sqr, cub, negate
- ...

And yeah - these all work perfectly for those strange 8-dimensional numbers - I mean you hopefully know that you can't do pretty much any of this with vectors for example - vectors have nothing to do with this. And there are many, many more features - including parsing textual formulas with the ability to set variables. And also hyper-complex angles - a great and (dare I say) complex topic on its own, and so on, and so on... There's a lot of useful code in there.

## Meaning
Complex number revolutionized physics and math, so are binary (aka split-complex) numbers starting to do so - at least to some extent. Also dual numbers have a lot of useful advantages.

Some real-world physics is not one-dimensional - such as electric voltage and current are not independant to one another - in fact they are one complex value (like you think of a particle having a mass - one-dimensional, but some things are complex numbers in reality).

So string theory says the universe has to have at least 11 dimensions (without time) or 12 dimensions (with time). So take a three-dimensional vector of a position, or better a four-dimensional space-time-vector and give it an 8-dimensional (as I call it:) ultra-complex value. It's quite possible that this would work out and for example simplify a lot of the math and equations and so on - just like complex numbers did.

For example the somehow hyperbolic-natured binary (aka split-complex or space-time) numbers are already used in physics to describe how waves are traveling in space. And those unspectacular dual numbers are used in mechanics and robotics to describe complex movements. Others of those eight dimensions share the *basic* attributes of one of those base-types, but in some ways they on their own behave uniquely. People have to look deeper into this - I'm afraid I'm neither a physicist nor a full-fledged mathematician, just a mere software engineer, who's interested in this and spent some spare time over a few years to constantly think about this - I wrote hundreds of pages of formulas and I think I'm really onto something. It's just that noone knows about this approach.

I hope some physics/math people will share my enthusiasm and try to verify or falsify my claim that these could be candidates for simplifying physics and/or fitting greatly into string-/m-theory and so on. The math, the formulas are the key - not this half-baken old code (yet still you won't find a better library for 8-dimensional combined hyper-complex math with complex, dual and binary numbers combined).
