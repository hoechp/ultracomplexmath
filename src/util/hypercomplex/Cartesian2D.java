package util.hypercomplex;

import java.util.Vector;

import util.tests.Tests;



/**
 * A two-dimensional cartesian vector.
 */
public class Cartesian2D extends Vector<Double> {
	
	/**
	 * serial version id
	 */
	private static final long serialVersionUID = 4750484305831683459L;
	
	/**
	 * constructor. constructs a vector with the cartesian values (0, 0).
	 */
	public Cartesian2D() {
		super();
		add(0d);
		add(0d);
	}
	
	/**
	 * Returns this (cartesian) vector.
	 * @return this (cartesian) vector
	 */
	public Cartesian2D getCartesian() {
		return this;
	}
	
	/**
	 * Returns the polynominal version of this vector.
	 * @return the polynominal version of this vector
	 */
	public Polynominal2D getPolynominal() {
		Polynominal2D result = new Polynominal2D();
		result.set(0, Math.sqrt(get(0) * get(0) + get(1) * get(1)));
		if (result.get(0) != 0) {
			if (get(1) < 0) {
				result.set(1, -Math.acos(get(0) / result.get(0)));
			} else {
				result.set(1, Math.acos(get(0) / result.get(0)));
			}
		} else {
			result.set(1, 0d);
		}
		return result;
	}

	/**
	 * Returns the dot product of this (cartesian) vector with the provided (cartesian) vector.
	 * @param other the other (cartesian) vector
	 * @return the dot product of this (cartesian) vector with the provided (cartesian) vector
	 */
	public double dot(Cartesian2D other) {
		return get(0) * other.get(0) + get(1) * other.get(1);
	}

	/**
	 * Returns the dot product of this (cartesian) vector with itself.
	 * @return the dot product of this (cartesian) vector with itself
	 */
	public double dot() {
		return dot(this);
	}

	/**
	 * Returns a vector that is the sum of this vector (cartesian) and the given (cartesian) vector.
	 * @param other the other (cartesian) vector
	 * @return a vector that is the sum of this vector (cartesian) and the given (cartesian) vector
	 */
	public Cartesian2D plus(Cartesian2D other) {
		Cartesian2D result = new Cartesian2D();
		for (int i = 0; i < 2; ++i) {
			result.set(i, get(i) + other.get(i));
		}
		return result;
	}

	/**
	 * Adds the given (cartesian) vector to this (cartesian) vector (changing its value).
	 * @param other the other (cartesian) vector
	 */
	public void add(Cartesian2D other) {
		for (int i = 0; i < 2; ++i) {
			set(i, get(i) + other.get(i));
		}
	}

	/**
	 * Returns a vector that is the difference of this (cartesian) vector and the given (cartesian) vector.
	 * @param other the other (cartesian) vector
	 * @return a vector that is the difference of this (cartesian) vector and the given (cartesian) vector
	 */
	public Cartesian2D minus(Cartesian2D other) {
		Cartesian2D result = new Cartesian2D();
		for (int i = 0; i < 2; ++i) {
			result.set(i, get(i) - other.get(i));
		}
		return result;
	}

	/**
	 * Substracts the given (cartesian) vector from this (cartesian) vector (changing its value).
	 * @param other the other (cartesian) vector
	 */
	public void substract(Cartesian2D other) {
		for (int i = 0; i < 2; ++i) {
			set(i, get(i) - other.get(i));
		}
	}

	/**
	 * Returns the x ordinate of this (cartesian) vector.
	 * @return the x ordinate of this (cartesian) vector
	 */
	public double getX() {
		return get(0);
	}

	/**
	 * Returns the y ordinate of this (cartesian) vector.
	 * @return the y ordinate of this (cartesian) vector
	 */
	public double getY() {
		return get(1);
	}
	
	/**
	 * Returns a String representing this (cartesian) vector.
	 */
	public String toString() {
		return toString('î');
	}
	
	/**
	 * Returns a String representing this (cartesian) vector.
	 * @param sign the sign used for the imaginary part
	 */
	public String toString(char sign) {
		boolean reZero = false;
		boolean imZero = false;
		if (Math.abs(get(0)) < Tests.DELTA) {
			reZero = true;
		}
		if (Math.abs(get(1)) < Tests.DELTA) {
			imZero = true;
		}
		String result = "";
		if (reZero && imZero) {
			result += "0";
		} else if (reZero && !imZero) {
			result += Tests.doubleWithFactorToString(get(1), "" + sign, false);
		} else if (!reZero && imZero) {
			result += Tests.doubleWithFactorToString(get(0), null, false);
		} else {
			result += Tests.doubleWithFactorToString(get(0), null, false) + (get(1) >= 0 ? " + " : " - ")
					+ Tests.doubleWithFactorToString(Math.abs(get(1)), "" + sign, false);
		}
		return result;
	}

}
