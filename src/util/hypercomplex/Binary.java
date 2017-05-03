package util.hypercomplex;


import java.util.ArrayList;


/**
 * A binary or hyperbolical or split-complex number. These terms are interchangeable.<br>
 * It represents a non-euclidean 2-dimensional algebra like complex numbers do, but here the dimensions have a different connection.<br>
 * Like complex numbers have î with î * î == -1, the binary numbers have Ê with Ê * Ê = 1.<br>
 * As the formula e^(a * î) = cos(a) + sin(a) * î is the key to understand complex numbers,<br>
 * the key to understand binary numbers is the formula e^(a * Ê) = cosh(a) + sinh(a) * Ê<br>
 * But unlike complex numbers, you can't display any binary as r * e^(a * Ê), unless r can be negative as well as complex.<br>
 * For simplicity I call numbers that can't be displayed that way numbers outside the main sector.<br>
 * <br>
 * Major restrictions are:<br>
 * - there is no logarithm of numbers outside the main sector.<br>
 * - you cannot raise a number outside the main sector to a non-integer or even part-imaginary power.<br>
 * <br>
 * But some things are easier, too:<br>
 * There are never an unlimited number of solutions when raising to a power or when taking a logarithm.<br>
 * Generally it is not more complicated than calculating with complex numbers.<br>
 * <br>
 * Numbers inside the main sector are Z = a + b * Ê with a > 0 and a > b.<br>
 * Those can be displayed as: length * e^(hyperbolic_angle * Ê)<br>
 * To display numbers outside the main sector, you need to multiply with -1 (turn 180°)<br>
 * and/or even mirror along the axis of f(x) = x by multiplying with Ê.<br>
 * In no way however, you can display something that way if its Z = a + b * Ê with abs(a) == abs(b).<br>
 * Those numbers have a third way of displaying - the diagonal form.<br>
 * There every number is displayed as a * (1 + Ê) / 2 + b * (1 - Ê) / 2.<br>
 * If you raise those bases ((1+Ê)/2, (1-Ê)/2) to any power, they stay the same - just like 1.<br>
 * So that would be the advantage of displaying a number that has no eulerian form in the diagonal form.
 * @author Philipp Kolodziej
 */
public class Binary extends Hypercomplex {
	
	private static final long serialVersionUID = 3551833257054940902L;
	
	/**
	 * binary number equaling the real number ONE
	 */
	public final static Binary ONE = new Binary(1);
	
	/**
	 * binary number equaling the real number ZERO
	 */
	public final static Binary ZERO = new Binary();
	
	/**
	 * binary number equaling the imaginary number I
	 */
	public final static Binary I = new Binary(0, 1);
	
	/**
	 * binary number equaling the real number E (== euler, not E == sqrt(1) != 1)
	 */
	public final static Binary E = new Binary(Math.E);
	
	/**
	 * binary number equaling (1 - E)/2 (E == sqrt(1) != 1)
	 */
	public final static Binary IDEMPOTENT_NEG = new Binary(0.5, -0.5);
	
	/**
	 * binary number equaling (1 - E)/2 (E == sqrt(1) != 1)
	 */
	public final static Binary E1 = IDEMPOTENT_NEG;
	
	/**
	 * binary number equaling (1 + E)/2 (E == sqrt(1) != 1)
	 */
	public final static Binary IDEMPOTENT_POS = new Binary(0.5, 0.5);
	
	/**
	 * binary number equaling (1 + E)/2 (E == sqrt(1) != 1)
	 */
	public final static Binary E2 = IDEMPOTENT_POS;
	
	/**
	 * Constructor. Constructs a binary number containing the provided parsable data.
	 * @param parseData the String-representation of the number
	 */
	public Binary(String parseData) {
		setCartesian(parseHypercomplex(parseData).getCartesian());
	}
	
	/**
	 * constructor. constructs a vector containing the cartesian and polynominal values (0, 0).
	 */
	public Binary() {
		super();
		setBinary(true);
	}

	/**
	 * Constructor. Constructs a real binary number containing the provided real value.
	 * @param re the real part
	 */
	public Binary(double re) {
		super(re);
		setBinary(true);
	}

	/**
	 * Constructor. Constructs a binary number containing the provided values.<br>
	 * <b>Note</b> the provided values will be treated as cartesian values.
	 * @param re the real part
	 * @param im the imaginary part
	 */
	public Binary(double re, double im) {
		super(re, im);
		setBinary(true);
	}

	/**
	 * Constructor. Constructs a complex number containing the provided values.<br>
	 * Use format == "p" or "P" and the values will be treated as polynominal.
	 * Use format == "c" or "C" and the values will be treated as cartesian.
	 * Use format == "r" or "R" and the values will be treated as a range.
	 * @param r the length, real part or range-start
	 * @param phi the angle, imaginary part or range-end
	 */
	public Binary(String format, double r, double phi) {
		if (format.equals("c") || format.equals("C")) {
			setCartesian(r, phi);
		} else if (format.equals("p") || format.equals("P")) {
			setPolynominal(r, phi);
		} else if (format.equals("r") || format.equals("R")) {
			setCartesian((phi + r) / 2, (phi - r) / 2);
		} else {
			setCartesian(Double.NaN, Double.NaN);
		}
		setBinary(true);
	}

	public double rangeFrom() { // TODO comment
		return x() - y();
	}
	public double rangeTo() { // TODO comment
		return x() + y();
	}
	public double rangeBase() { // TODO comment
		return x();
	}
	public double rangeRadius() { // TODO comment
		return y();
	}

	/**
	 * Converts Complex into Binary
	 * @param c the complex number to convert
	 * @return the binary number
	 */
	public static Binary binary(Hypercomplex c) {
		return new Binary(c.re(), c.im());
	}
	
	/**
	 * Binary exponential function. Returns e^x with x being the binary exponent.
	 * @param x the binary exponent
	 * @return e^x with x being the binary exponent
	 */
	public static Binary exp(Hypercomplex x) {
		return E.pow(x);
	}

	/**
	 * Binary natural logarithm. Returns ln(x) with x being the binary argument.
	 * @param x the binary argument
	 * @return ln(x) with x being the binary argument
	 */
	public static Binary ln(Hypercomplex x) {
		return binary(x).ln();
	}

	/**
	 * Binary logarithm of x to the base of b.
	 * Returns log_b(x) with x being the binary argument, b being the binary base.
	 * @param b the binary base
	 * @param x the binary argument
	 * @return log_b(x) with x being the binary argument, b being the binary base
	 */
	public static Binary log(Hypercomplex b, Hypercomplex x) {
		return binary(x).log(b);
	}

	/**
	 * Binary power. Returns x to the power of w.
	 * @param x the binary base
	 * @param w the binary exponent
	 * @return x to the power of w
	 */
	public static Binary pow(Hypercomplex x, Hypercomplex w) {
		return binary(x).pow(w);
	}

	/**
	 * Binary power. Returns x to the power of w.
	 * @param x the binary base
	 * @param w the real exponent
	 * @return x to the power of w
	 */
	public static Binary pow(Hypercomplex x, double w) {
		return binary(x).pow(w);
	}

	/**
	 * Principal value of the binary square root. Returns the principal square root of x.
	 * @param x the provided binary number
	 * @return the principal square root of x
	 */
	public static Binary sqrt(Hypercomplex x) {
		return binary(x).pow(0.5);
	}
	
	/**
	 * Returns a vector that is the sum of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the sum of this vector and the given vector
	 */
	public Binary plus(Hypercomplex other) {
		return new Binary(re() + other.re(), im() + other.im());
	}

	/**
	 * Returns a vector that is the difference of this vector and the given vector.
	 * @param other the other vector
	 * @return a vector that is the difference of this vector and the given vector
	 */
	public Binary minus(Hypercomplex other) {
		return new Binary(re() - other.re(), im() - other.im());
	}

	/**
	 * Returns a vector that is the product of this vector and the given factor.
	 * @param factor the factor
	 * @return a vector that is the product of this vector and the given factor
	 */
	public Binary times(double factor) {
		return new Binary(re() * factor, im() * factor);
	}

	/**
	 * Returns a vector that is the quotient of this vector and the given divisor.
	 * @param divisor the divisor
	 * @return a vector that is the quotient of this vector and the given divisor
	 */
	public Binary by(double divisor) {
		return new Binary(re() / divisor, im() / divisor);
	}

	/**
	 * Returns a binary number that is the (binary) inverse of this binary number.
	 * @return a binary number that is the (binary) inverse of this binary number
	 */
	public Binary inverse() {
		return conjugate().by(det());
	}

	/**
	 * Returns a binary number that is the binary conjugate of this binary number.
	 * @return a binary number that is the binary conjugate of this binary number
	 */
	public Binary conjugate() {
		return new Binary(re(), -im());
	}

	/**
	 * Returns an ArrayList of the n binary numbers that are the n-th roots of this binary number.
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return an ArrayList of the n binary numbers that are the n-th roots of this binary number
	 */
	public ArrayList<? extends Hypercomplex> roots(int n) {
		return pow(1, n);
	}

	/**
	 * Returns an ArrayList of the n binary numbers that are this to the power of (a / n).
	 * @param a the numerator
	 * @param n the denominator
	 * @return an ArrayList of the n binary numbers that are this to the power of (a / n)
	 */
	public ArrayList<? extends Hypercomplex> pow(int a, int n) {
		if (n == 0) { // if the denominator is zero dividing through it is impossible
			return null;
		}
		if (n < 0) { // n must be positive, a can be negative
			a *= -1;
			n *= -1;
		}		
		int gcd, h0, h1 = Math.abs(a), h2 = n;
	    while (true) { // Euklid's GCD iterative
	        if (h2 == 0) {
	        	gcd = h1;
	        	break;
	        } else {
	        	h0 = h1 % h2;
	        	h1 = h2;
	        	h2 = h0;
	        }
	    }
	    a /= gcd;
	    n /= gcd;
	    // now since a and n are proper now the recognizable slightly modified complex roots formula comes to use
		ArrayList<Binary> result = new ArrayList<Binary>();
		Binary base = pow(a);
	    if (n % 2 == 0) {
	    	// type a^(1/n) == +-abs(a)^(1/n), +-E(abs(a)^(1/n)) <-- if d == 1, else its n.def.
	    	ArrayList<Double> hyp = base.hyperbolicForm();
	    	Binary d = new Binary(hyp.get(1), hyp.get(2));
	    	if (!d.equals(ONE)) {
	    		return null;
	    	} else {
	    		double r = hyp.get(0);
	    		double phi = hyp.get(3);
	    		Binary res1 = new Binary(0, phi / n).exp().times(Math.pow(r, 1d / n));
	    		result.add(res1);
	    		result.add(res1.times(-1));
	    		result.add(res1.times(I));
	    		result.add(res1.times(I).times(-1));
	    		return result;
	    	}
	    } else {
	    	// type a^(1/n) == sign(a) * abs(a)^(1/n) <-- with sign(a) including directions Ê and -Ê
	    	ArrayList<Double> hyp = base.hyperbolicForm();
	    	Binary d = new Binary(hyp.get(1), hyp.get(2));
    		double r = hyp.get(0);
    		double phi = hyp.get(3);
    		result.add(new Binary(0, phi / n).exp().times(Math.pow(r, 1d / n)).times(d));
    		return result;
	    }
	}
	
	/**
	 * Returns a binary number that is this binary number to the power p.
	 * @param p the power
	 * @return a binary number that is this binary number to the power p
	 */
	public Binary pow(double p) {
		return pow(new Binary(p, 0));
	}
	
	/**
	 * Returns the value of e to the power of this binary number.
	 * @return the value of e to the power of this binary number
	 */
	public Binary exp() {
		return new Binary(Math.cosh(im()), Math.sinh(im())).times(Math.exp(re()));
	}
	
	/**
	 * Returns the natural logarithm of this binary number.
	 * @return the natural logarithm of this binary number
	 */
	public Binary ln() {
		if (Math.abs(phi()) >= Math.PI / 4) {
			return null;
		}
		double r = Math.sqrt(det());
		Binary normal = this.by(r);
		double phi = asinh(normal.im());
		return new Binary(Math.log(r), phi);
	}
	
	/**
	 * Binary logarithm of this to the base of b.
	 * Returns log_b(this) with b being the binary base.
	 * @param b the binary base
	 * @return log_b(this) with b being the binary base
	 */
	public Binary log(Hypercomplex b) {
		Binary result = ln().by(b.ln());
		Binary principalHolder = new Binary("p", 0, result.im());
		result.setImaginary(principalHolder.phi());
		return result;
	}
	
	/**
	 * Returns the value of this binary number to the power of the other provided binary exponent.
	 * @param w the binary exponent
	 * @return the value of this binary number to the power of the other provided binary exponent
	 */
	public Binary pow(Hypercomplex w) {
		if (Math.abs(phi()) > Math.PI / 4 && !w.isRealInteger()) {
			//System.err.println("invalid split-complex power operation (" + this + ")^(" + w + "): " +
			//		"exponent needs to be Z = a + bE with (a + b) being integer (or base needs to have a > 0, a > abs(b)).");
			return null;
		} else {
			if (Math.abs(phi()) < Math.PI / 4) {
				return ln().times(w).exp();
			} else {
				if ((int)Math.abs(w.re()) % 2 == 0) {
			    	// type a^n == abs(a)^n
					Binary base = this.times(eulerDirection());
					return base.ln().times(w).exp();
				} else {
			    	// type a^n == sign(a) * abs(a)^n
					Binary base = this.times(eulerDirection());
					return base.ln().times(w).exp().times(eulerDirection());
				}
			}
		}
	}

	/**
	 * Returns true if this binary number is the natural logarithm of the other binary number
	 * @param other the other binary number
	 * @return true if this binary number is the natural logarithm of the other binary number, otherwise false
	 */
	public boolean isLn(Hypercomplex other) {
		return other.ln().equals(this);
	}

	/**
	 * Returns true if this binary number is the
	 * logarithm to the provided base of the other binary number
	 * @param base the binary base
	 * @param other the other binary number
	 * @return true if this binary number is the
	 * logarithm to the provided base of the other binary number, otherwise false
	 */
	public boolean isLog(Hypercomplex base, Hypercomplex other) {
		return other.log(base).equals(this);
	}

	/**
	 * Returns true if this binary number is the binary number that is x to the power of w<br>
	 * <b>Note</b> that if the exponent is real there are infinite solutions,
	 * using the function isPow(Complex x, int a, int n) however checks for a finite number of solutions.
	 * @param x the binary base
	 * @param w the binary exponent
	 * @return true if this binary number is the binary number that is x to the power of w
	 */
	public boolean isPow(Hypercomplex x, Hypercomplex w) {
		return x.pow(w).equals(this);
	}

	/**
	 * Returns true if this is x to the power of (a / n).
	 * @param x the binary base
	 * @param a the numerator of the exponent
	 * @param n the denominator of the exponent
	 * @return true if this is x to the power of (a / n) otherwise false
	 */
	public boolean isPow(Hypercomplex x, int a, int n) {
		return binary(x).pow(a, n).contains(this);
	}

	/**
	 * Returns true if this is the n-th root of x.
	 * @param x the binary base
	 * @param n the root index (for example: n == 2 -> square root)
	 * @return true if this is the n-th root of x otherwise false
	 */
	public boolean isRoot(Hypercomplex x, int n) {
		return binary(x).roots(n).contains(this);
	}

	/**
	 * Returns a copy of the vector that is that is turned by the provided angle.
	 * @param rad the (radian) angle
	 * @return a copy of the vector that is that is turned by the provided angle
	 */
	public Binary turnedBy(double rad) {
		return binary(turnedBy(rad));
	}
	
	/**
	 * Returns a copy of this vector with the length of 1.
	 * @return a copy of this vector with the length of 1
	 */
	public Binary r0() {
		return by(length());
	}
	
	/**
	 * Returns a copy of this vector with the length of the old length to the power of n.
	 * @param n the power
	 * @return a copy of this vector with the length of the old length to the power of n
	 */
	public Binary r(double n) {
		return times(Math.pow(r(), n) / length());
	}

	/**
	 * Returns the vector with the contribution of this vector in direction of the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector in direction of the provided vector
	 */
	public Binary partInDirection(Hypercomplex r) {
		return binary(r).times(r.dot(this) / r.dot());
	}

	/**
	 * Returns the vector with the contribution of this vector orthogonally to the provided vector.
	 * @param r the vector carrying the direction
	 * @return the vector with the contribution of this vector orthogonally to the provided vector
	 */
	public Binary partOrthogonallyTo(Hypercomplex r) {
		return minus(partInDirection(r));
	}

	/**
	 * Hilbert-Gram's Orthogonalization.<br>
	 * Divides a vector into the part in a direction and the rest.
	 * @param r direction to split in
	 * @return an arraylist with two vectors.<br>
	 * the first one holds the part in direction of r,<br>
	 * the other one holds the rest of the original vector.
	 */
	public ArrayList<? extends Hypercomplex> hilbert(Hypercomplex r) {
		ArrayList<Binary> result = new ArrayList<Binary>();
		result.add(partInDirection(r));
		result.add(binary(r).minus(result.get(0)));
		return result;
	}

	/**
	 * Returns this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored radial to the provided position (mirrored on an axis orthogonal to this.minus(r))
	 */
	public Binary mirroredRadialTo(Hypercomplex r) {
		return this.minus(partInDirection(r).times(2));
	}

	/**
	 * Returns this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r)).
	 * @param r the other position
	 * @return this vector mirrored orthogonal to the provided position (mirrored on an axis radial to this.minus(r))
	 */
	public Binary mirroredOrthogonalTo(Hypercomplex r) {
		return partInDirection(r).times(2).minus(this);
	}
	
	/**
	 * Returns a binary number that is the (binary) product of this binary number and the given binary factor.
	 * @param f the (binary) factor
	 * @return a binary number that is the (binary) product of this binary number and the given binary factor
	 */
	public Binary times(Hypercomplex f) {
		return new Binary(re() * f.re() + im() * f.im(), re() * f.im() + im() * f.re());
	}

	/**
	 * Returns a binary number that is the (binary) quotient of this binary number and the given binary divisor.
	 * @param d the (binary) divisor
	 * @return a binary number that is the (binary) quotient of this binary number and the given binary divisor
	 */
	public Binary by(Hypercomplex d) {
		return new Binary((re() * d.re() - im() * d.im()) / d.det(), (im() * d.re() - re() * d.im()) / d.det());
	}

	/**
	 * Returns the determinant of this binary number.
	 * @return the determinant of this binary number
	 */
	public double det() {
		return re() * re() - im() * im();
	}

	/**
	 * Returns a String representing this binary number.
	 * @return a String representing this binary number
	 */
	@Override
	public String toString() {
		return getCartesian().toString('Ê');
	}
	
	/**
	 * Returns a representation of this number as (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E)).<br>
	 * So the returned (A, B) can be used for easy multiplication: (A, B)*(C, D)=(A*C, B*D).
	 * @return a representation of this number as (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E))
	 */
	public ArrayList<Double> diagonalBasis() {
		ArrayList<Double> result = new ArrayList<Double>();
		result.add(re() - im());
		result.add(re() + im());
		return result;
	}
	
	/**
	 * Returns a representation of this number as (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E)).<br>
	 * So the returned (A, B) can be used for easy multiplication: (A, B)*(C, D)=(A*C, B*D).
	 * @return a representation of this number as (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E))
	 */
	public ArrayList<Double> nullBasis() {
		return diagonalBasis();
	}
	
	/**
	 * Returns a binary number from a representation of this number with (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E)).<br>
	 * So (A, B) can be used for easy multiplication: (A, B)*(C, D)=(A*C, B*D).
	 * @param a the factor for (1 - E)/2
	 * @param b the factor for (1 + E)/2
	 */
	public static Binary fromDiagonalBasis(double a, double b) {
		return E1.times(a).plus(E2.times(b));
	}
	
	/**
	 * Returns a binary number from a representation of this number with (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E)).<br>
	 * So (A, B) can be used for easy multiplication: (A, B)*(C, D)=(A*C, B*D).
	 * @param a the factor for (1 - E)/2
	 * @param b the factor for (1 + E)/2
	 */
	public static Binary fromNullBasis(double a, double b) {
		return fromDiagonalBasis(a, b);
	}
	
	/**
	 * Returns a representation of this number as R * (D_R + D_I * E) * e^(phi * E).<br>
	 * Specifically it returns the parameters R, D_R, D_I, phi.<br>
	 * E is the base of the imaginary part of the split-complex (or hyperbolic) numbers: E * E == 1 && E != 1
	 * @return the parameters R, D_R, D_I, phi of the representation of this number as (A * (1/2 - 1/2*E) + B * (1/2 + 1/2*E))
	 */
	public ArrayList<Double> hyperbolicForm() {
		ArrayList<Double> result = new ArrayList<Double>();
		result.add(eulerLength());
		Binary d = eulerDirection();
		result.add(d.re());
		result.add(d.im());
		result.add(eulerAngle());
		return result;
	}
	
	/**
	 * Contructs and returns a binary number from its eulerian form / hyperlic form.
	 * rAbs tells the absolute eulerian distance
	 * Either dI must be -1 or 1 and dR == 0, or dR must be -1 or 1 and dI == 0.
	 * So dR and dI combined tell the direction (positive/negative real-/imaginary-axis).
	 * dR == 0, dI == 0 would be possible to obtain zero, but that should not be useful.
	 * Other values for dR, dI should usually make no sense.
	 * @param rAbs the absolute eulerian length
	 * @param dR the sign (-1, 0 or 1) of the real part of the direction
	 * @param dI the sign (-1, 0 or 1) of the real part of the direction
	 * @param phi the eulerian / hyperbolic angle
	 * @return a binary number from its eulerian form / hyperlic form
	 */
	public static Binary fromHyperbolicForm(double rAbs, double dR, double dI, double phi) {
		Binary direction = new Binary(dR, dI);
		Binary result = new Binary(Math.cosh(phi), Math.sinh(phi));
		return result.times(direction).times(rAbs);
	}

	/**
	 * Returns the angle phi for the Z = r * d * e^(phi * E) equation (positive r, potentially negative d).
	 * @return the angle phi for the Z = r * d * e^(phi * E) equation (positive r, potentially negative d)
	 */
	public double eulerAngle() {
		Binary normal = this.by(eulerLength()).times(eulerDirection());
		double phi = asinh(normal.im()); // = acosh(normal.re());
		return phi;
	}
	
	/**
	 * Returns the length r for the Z = r * d * e^(phi * E) equation (positive r, potentially negative d).
	 * @return the length r for the Z = r * d * e^(phi * E) equation (positive r, potentially negative d)
	 */
	public double eulerLength() {
		return Math.sqrt(Math.abs(det()));
	}
	
	/**
	 * Returns the direction d for the Z = r * d * e^(phi * E) equation (positive r, potentially negative d).
	 * @return the direction d for the Z = r * d * e^(phi * E) equation (positive r, potentially negative d)
	 */
	public Binary eulerDirection() {
		double dR = 0, dI = 0;
		if (phi() > 3 * Math.PI / 4 || phi() < -3 * Math.PI / 4) {
			dR = -1;
		} else if (phi() < Math.PI / 4 && phi() > -Math.PI / 4) {
			dR = 1;
		} else if (Math.abs(phi()) < 3 * Math.PI / 4 && Math.abs(phi()) > Math.PI / 4) {
			dR = 0;
		} else {
			dR = Double.NaN; // those numbers have no hyperbolic form
			//System.err.println("error with dR: " + this + "(phi == " + phi() / Math.PI + "*PI)");
			return null;
		}
		if (phi() < 3 * Math.PI / 4 && phi() > Math.PI / 4) {
			dI = 1;
		} else if (phi() < -Math.PI / 4 && phi() > -3 * Math.PI / 4) {
			dI = -1;
		} else if (Math.abs(phi()) > 3 * Math.PI / 4 || Math.abs(phi()) < Math.PI / 4) {
			dI = 0;
		} else {
			dI = Double.NaN; // those numbers have no hyperbolic form
			//System.err.println("error with dI " + this + "(phi == " + phi() / Math.PI + "*PI)");
			return null;
		}
		return new Binary(dR, dI);
	}

	// ------------------------- MERE SETTER FUNCTIONS (USING OTHER METHODS) -------------------------

	/**
	 * Multiplies this vector with the given factor (changing its value).
	 * @param factor the factor
	 */
	public void multiply(double factor) {
		set(times(factor));
	}

	/**
	 * Divides the given vector to this vector (changing its value).
	 * @param divisor the divisor
	 */
	public void divide(double divisor) {
		set(by(divisor));
	}

	// ------------------------- TRIGONOMETRIC FUNCTIONS -------------------------
	
	/**
	 * sine
	 * @return sine
	 */
	public Binary sin() {
		return new Binary(Math.sin(re()) * Math.cos(im()), Math.cos(re()) * Math.sin(im()));
	}

	/**
	 * cosine
	 * @return cosine
	 */
	public Binary cos() {
		return new Binary(Math.cos(re()) * Math.cos(im()), -Math.sin(re()) * Math.sin(im()));
	}

	/**
	 * hyperbolic sine
	 * @return hyperbolic sine
	 */
	public Binary sinh() {
		return new Binary(Math.sinh(re()) * Math.cosh(im()), Math.cosh(re()) * Math.sinh(im()));
	}

	/**
	 * hyperbolic cosine
	 * @return hyperbolic cosine
	 */
	public Binary cosh() {
		return new Binary(Math.cosh(re()) * Math.cosh(im()), Math.sinh(re()) * Math.sinh(im()));
	}

	/**
	 * inverse sine
	 * @return inverse sine
	 */
	public Binary asin() {
		double arg1 = Math.sqrt(Math.pow(re() * re() - im() * im() - 1, 2) - 4 * im() * im());
		double arg2 = re() * re() - im() * im();
		return new Binary(Math.signum(re()) / 2 * Math.acos(arg1 - arg2),
				Math.signum(im()) / 2 * Math.acos(arg1 + arg2));
	}

	/**
	 * inverse cosine
	 * @return inverse cosine
	 */
	public Binary acos() {
		return asin().times(-1).plus(new Binary(Math.PI / 2, 0));
	}
	
	// tan = sin / cos, COS(ATAN(X)) == (X^2 + 1)^(-1 / 2) => ATAN(X) == ACOS((X^2 + 1)^(-1 / 2))
	/**
	 * inverse tangent
	 * @return inverse tangent
	 */
	public Binary atan() {
		return times(this).plus(ONE).pow(-0.5d).acos();
	}

	/**
	 * inverse cotangent
	 * @return inverse cotangent
	 */
	public Binary acot() {
		return new Binary(Math.PI / 2).minus(atan());
	}

	/**
	 * inverse secant
	 * @return inverse secant
	 */
	public Binary asec() {
		return inverse().acos();
	}

	/**
	 * inverse cosecant
	 * @return inverse cosecant
	 */
	public Binary acsc() {
		return inverse().asin();
	}

	/**
	 * inverse hyperbolic sine
	 * @return inverse hyperbolic sine
	 */
	public Binary asinh() {
		Binary sqrt = times(this).plus(ONE).pow(0.5);
		if (sqrt == null) {
			return null;
		}
		return plus(sqrt).ln();
	}

	/**
	 * inverse hyperbolic cosine
	 * @return inverse hyperbolic cosine
	 */
	public Binary acosh() {
		Binary sqrt = times(this).minus(ONE).pow(0.5);
		if (sqrt == null) {
			return null;
		}
		return plus(sqrt).ln();
	}
	
	/**
	 * inverse hyperbolic tangent
	 * @return inverse hyperbolic tangent
	 */
	public Binary atanh() {
		return plus(ONE).by(ONE.minus(this)).ln().by(2);
	}
	
}
