package util.hypercomplex;


import java.util.Formatter;
import java.util.Vector;



/**
 * A two-dimensional polynominal vector.<br>
 * A positive length (length >= 0) is ensured.<br>
 * A normalized angle between -PI and PI (-PI < direction <= PI) is also ensured.
 */
public class Polynominal2D extends Vector<Double> {

	/**
	 * serial version id
	 */
	private static final long serialVersionUID = -3634400522097878038L;

	/**
	 * constructor. constructs a vector with the polynominal values (0, 0).
	 */
	public Polynominal2D() {
		super();
		this.add(0d);
		this.add(0d);
	}
	
	/**
	 * Returns this (polynominal) vector.
	 * @return this (polynominal) vector
	 */
	public Polynominal2D getPolynominal() {
		return this;
	}
	
	/**
	 * Returns the cartesian version of this vector.
	 * @return the cartesian version of this vector
	 */
	public Cartesian2D getCartesian() {
		Cartesian2D result = new Cartesian2D();
		result.set(0, get(0) * Math.cos(get(1)));
		result.set(1, get(0) * Math.sin(get(1)));
		return result;
	}

	/**
	 * Ensures that direction is positive and direction between -PI and PI.
	 */
	public void checkDirectionAndAngle() {
		if (this.get(0) < 0) {
			this.set(0, -this.get(0));
			this.set(1, this.get(1) + Math.PI);
		}
		if (this.get(1) > Math.PI) { // keep below PI
			this.set(1, this.get(1) % (2 * Math.PI));
			if (this.get(1) > Math.PI) {
				this.set(1, this.get(1) - (2 * Math.PI));
			}
		}
		if (this.get(1) < -Math.PI) { // keep above -PI
			this.set(1, this.get(1) % (-2 * Math.PI));
			if (this.get(1) < -Math.PI) {
				this.set(1, this.get(1) - (-2 * Math.PI));
			}
		}
	}

	/**
	 * Returns a vector that is the product of this (polynominal) vector and the given factor.
	 * @param factor the factor
	 * @return a vector that is the product of this (polynominal) vector and the given factor
	 */
	public Polynominal2D times(double factor) {
		Polynominal2D result = new Polynominal2D();
		result.set(0, factor * get(0));
		result.set(1, get(1));
		checkDirectionAndAngle();
		return result;
	}

	/**
	 * Multiplies this (polynominal) vector with the given factor (changing its value).
	 * @param factor the factor
	 */
	public void multiply(double factor) {
		set(0, factor * get(0));
		checkDirectionAndAngle();
	}

	/**
	 * Returns a vector that is the quotient of this (polynominal) vector and the given divisor.
	 * @param divisor the divisor
	 * @return a vector that is the quotient of this (polynominal) vector and the given divisor
	 */
	public Polynominal2D by(double factor) {
		Polynominal2D result = new Polynominal2D();
		result.set(0, get(0) / factor);
		result.set(1, get(1));
		checkDirectionAndAngle();
		return result;
	}

	/**
	 * Divides the given vector to this (polynominal) vector (changing its value).
	 * @param divisor the divisor
	 */
	public void divide(double factor) {
		set(0, get(0) / factor);
		checkDirectionAndAngle();
	}

	/**
	 * Returns a copy of this vector (polynominal) that is that is turned by the provided angle.
	 * @param rad the (radian) angle
	 * @return a copy of this (polynominal) vector that is that is turned by the provided angle
	 */
	public Polynominal2D turnedBy(double angle) {
		Polynominal2D result = new Polynominal2D();
		result.set(0, get(0));
		result.set(1, get(1) + angle);
		checkDirectionAndAngle();
		return result;
	}

	/**
	 * Turns this (polynominal) vector by the provided angle.
	 * @param rad the (radian) angle
	 */
	public void turn(double angle) {
		set(1, get(1) + angle);
		checkDirectionAndAngle();
	}
	
	/**
	 * Returns the length of this (polynominal) vector.
	 * @return the length of this (polynominal) vector
	 */
	public double getLength() {
		return get(0);
	}
	
	/**
	 * Returns the (radian) angle/direction of this (polynominal) vector.
	 * @return the (radian) angle/direction of this (polynominal) vector
	 */
	public double getDirection() {
		return get(1);
	}
	
	/**
	 * Returns a String representing this (polynominal) vector.
	 */
	public String toString() {
		StringBuilder sb = new StringBuilder();
		Formatter formatter = new Formatter(sb);
		String format = "%." + Hypercomplex.DISPLAYED_CIPHER_COUNT + "g";
		formatter.format(format + " e^(" + format + " pi î)",
				get(0), get(1) / Math.PI);
		formatter.close();
		return sb.toString();
	}
	
}
