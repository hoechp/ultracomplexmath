package util.ds;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Random;

/**
 * implements square roots as written integer square root with remainder and fermat-factorization.
 */
public class BigInt extends BigInteger {

	private static final long serialVersionUID = 3461959037955498952L;

	public BigInt(String val) {
		super(val);
	}

	/**
	 * small pairs of square numbers used in the method of the written integer square root with remainder
	 */
	private static final int[][] SMALL_SQUARE_PAIRS = {{0, 0}, {1, 1}, {2, 4}, {3, 9}, {4, 16}, {5, 25}, {6, 36}, {7, 49}, {8, 64}, {9, 81}};
	
	/**
	 * the precision to check for probable primes
	 */
	private static final int PRIME_PRECISION = 100;

	public final static BigInteger ONE = new BigInteger("1");
	public final static BigInteger TWO = new BigInteger("2");
	public final static BigInteger THREE = new BigInteger("3");
	public final static BigInteger TEN = new BigInteger("10");
	public final static BigInteger TWENTY = new BigInteger("20");
	public final static BigInteger HUNDRED = new BigInteger("100");
	
	/**
	 * Takes an ArrayList of BigInteger, either 2 numbers, that are the fermat factors,
	 * or 3 numbers, that also include the number of iterations it took to calculate those factors,
	 * and returns an output String for the calculation.
	 * @param input the fermat input
	 * @return an output String
	 */
	public static String fermatOutput(ArrayList<BigInteger> input) {
		StringBuffer sb = new StringBuffer();
		StringBuffer sbEnd = new StringBuffer();
		if (input.size() == 3) {
			sbEnd.append(" (calculated in " + input.get(0) + " step" + (input.get(0).intValue() != 1 ? "s" : "") + ")");
		} else if (input.size() == 2) {
		} else {
			return "ERROR";
		}
		sb.append("" + input.get(input.size() == 3 ? 1 : 0).multiply(input.get(input.size() == 3 ? 2 : 1)) + " = "
				+ input.get(input.size() == 3 ? 1 : 0) + " * " + input.get(input.size() == 3 ? 2 : 1));
		if (input.get(input.size() == 3 ? 1 : 0).add(input.get(input.size() == 3 ? 2 : 1)).remainder(TWO).compareTo(ONE) != 0) {
			sb.append(" with factors " + input.get(input.size() == 3 ? 1 : 0).add(input.get(input.size() == 3 ? 2 : 1)).divide(TWO) + " +- "
					+ input.get(input.size() == 3 ? 2 : 1).subtract(input.get(input.size() == 3 ? 1 : 0).add(input.get(input.size() == 3 ? 2 : 1)).divide(TWO)));
		} else {
			sb.append(" (though the fermat-method is not applicable to this number)");
		}
		sb.append(sbEnd);
		return sb.toString();
	}
	
	/**
	 * Finds the next probable prime of a given BigInteger.
	 * @param number the given number
	 * @return the next probable prime
	 */
	public static BigInteger nextPrime(BigInteger number) {
		if (number.compareTo(ONE) <= 0) {
			return TWO;
		}
		if (number.remainder(TWO).compareTo(ONE) != 0) {
			number = number.subtract(ONE);
		}
		BigInteger p = null;
		for (BigInteger n = number.add(TWO);; n = n.add(TWO)) {
			if (n.isProbablePrime(PRIME_PRECISION)) {
				p = n;
				break;
			}
		}
		return p;
	}
	
	/**
	 * Fermat-factorizes a given BigInteger to two factors.
	 * @param number the given BigInteger
	 * @return an ArrayList of BigInteger with the factors
	 */
	public static ArrayList<BigInteger> fermatFactors(BigInteger number) {
		return fermatFactors(number, false);
	}

	/**
	 * Fermat-factorizes a given BigInteger to two factors.
	 * If advancedOutput == true the function will also include the number of iterations in the ArrayList
	 * (it then will be the first entry).
	 * @param number the given BigInteger
	 * @param advancedOutput parameter to also return the number of iterations.
	 * @return an ArrayList of BigInteger with the factors and if wanted the number of iterations.
	 */
	public static ArrayList<BigInteger> fermatFactors(BigInteger number, boolean advancedOutput) {
		ArrayList<BigInteger> list = new ArrayList<BigInteger>();
		BigInteger maximumX = (number.remainder(TWO).compareTo(ONE) != 0) ? number.divide(TWO).add(TWO).divide(TWO) : number.divide(THREE).add(THREE).divide(TWO);
		BigInteger x = ceiledRoot(number);
		BigInteger r = x.pow(2).subtract(number);
		int debugCounter = 1;
		BigInteger y = root(r);
		while (y == null && r.compareTo(BigInteger.ZERO) != 0) {
			++debugCounter;
			if (x.compareTo(maximumX) > 0) { // failed
				if (advancedOutput) {
					list.add(new BigInteger("" + debugCounter));
				}
				list.add(ONE);
				list.add(number);
				return list;
			}
			r = r.add(x.multiply(TWO).add(ONE));
			x = x.add(ONE);
			y = root(r);
		}
		BigInteger a = x.subtract(y);
		BigInteger b = x.add(y);
		if (advancedOutput) {
			list.add(new BigInteger("" + debugCounter));
		}
		list.add(a);
		list.add(b);
		return list;
	}
	
	/**
	 * Gives the number x with sqrt(x) == number. So it gives the exact square root or null if impossible.
	 * This uses the method of the written square root calculation and stops at the precision of 1 to get the integer value.
	 * @param number the given input
	 * @return the exact square root
	 */
	public static BigInteger root(BigInteger number) {
		return root(number, 0);
	}
	
	/**
	 * Gives the smallest number >= x with sqrt(x) == number. So it gives the floored square root.
	 * This uses the method of the written square root calculation and stops at the precision of 1 to get the integer value.
	 * @param number the given input
	 * @return the floored square root
	 */
	public static BigInteger flooredRoot(BigInteger number) {
		return root(number, -1);
	}
	
	/**
	 * Gives the smallest number >= x with sqrt(x) == number. So it gives the ceiled square root.
	 * This uses the method of the written square root calculation and stops at the precision of 1 to get the integer value.
	 * @param number the given input
	 * @return the square root from the given direction
	 */
	public static BigInteger ceiledRoot(BigInteger number) {
		return root(number, 1);
	}
	
	/**
	 * Gives the smallest number >= x with sqrt(x) == number. So it gives the ceiled square root.
	 * This uses the method of the written square root calculation and stops at the precision of 1 to get the integer value.
	 * @param number the given input
	 * @param direction if direction < 0 the floored root will be calculated,
	 * 		if direction > 0 the ceiled root will be calculated,
	 * 		if direction == 0 the exact root will be calculated or null will be returned
	 * @return the square root from the given direction
	 */
	public static BigInteger root(BigInteger number, int direction) {
		String name = number.toString();
		int blocks = (name.length() + 1) / 2;
		BigInteger n = new BigInteger("" + block(number, blocks - 1));
		BigInteger x = new BigInteger("" + lessThanHundredSquareBase(n.intValue()));
		BigInteger r = n.subtract(x.pow(2));
		BigInteger b;
		for (int i = blocks - 2; i >= 0; --i) {
			n = new BigInteger("" + block(number, i));
			r = r.multiply(HUNDRED).add(n);
			b = r.divide(x.multiply(TWENTY));
			while (x.multiply(TWENTY).add(b).multiply(b).compareTo(r) > 0) {
				b = b.subtract(ONE);
			}
			r = r.subtract(x.multiply(TWENTY).add(b).multiply(b));
			x = x.multiply(TEN).add(b);
		}
		if (direction > 0 && !r.equals(BigInteger.ZERO)) {
			x = x.add(ONE);
		}
		if (direction == 0 && !r.equals(BigInteger.ZERO)) {
			return null;
		}
		return x;
	}
	
	/**
	 * Gives the integer root and remainder.
	 * This uses the method of the written square root calculation and stops at the precision of 1 to get the integer value.
	 * @param number the given input
	 * @return an ArrayList of BigInteger with the integer root and remainder
	 */
	public static ArrayList<BigInteger> rootAndRemainder(BigInteger number) {
		String name = number.toString();
		int blocks = (name.length() + 1) / 2;
		BigInteger n = new BigInteger("" + block(number, blocks - 1));
		BigInteger x = new BigInteger("" + lessThanHundredSquareBase(n.intValue()));
		BigInteger r = n.subtract(x.pow(2));
		BigInteger b;
		for (int i = blocks - 2; i >= 0; --i) {
			n = new BigInteger("" + block(number, i));
			r = r.multiply(HUNDRED).add(n);
			b = r.divide(x.multiply(TWENTY));
			while (x.multiply(TWENTY).add(b).multiply(b).compareTo(r) > 0) {
				b = b.subtract(ONE);
			}
			r = r.subtract(x.multiply(TWENTY).add(b).multiply(b));
			x = x.multiply(TEN).add(b);
		}
		ArrayList<BigInteger> result = new ArrayList<BigInteger>();
		result.add(x);
		result.add(r);
		return result;
	}

	/**
	 * Determines if the given input number is a square number.
	 * This uses the method of the written square root calculation and stops at the precision of 1 to get the integer value.
	 * It then checks for the remainder.
	 * @param number the given input
	 * @return true if the number is square, otherwise false
	 */
	public static boolean isSquare(BigInteger number) {
		return root(number) != null;
	}
	
	/**
	 * Gives the specified block (counting from the back of the number, beginning with 0).
	 * @param number the input number
	 * @param place the specified place
	 * @return the block
	 */
	private static int block(BigInteger number, int place) {
		// 0 -> % 100 - % 1 / 1
		// 1 -> % 10000 - % 100 / 100
		return number.remainder(HUNDRED.pow(place + 1)).subtract(number.remainder(HUNDRED.pow(place))).divide(HUNDRED.pow(place)).intValue();
	}
	
	/**
	 * Gives the biggest number <= x with x^2 == number <b>if the number is less than 100</b>.
	 * So it gives the floored square number base <b>if the number is less than 100</b>.
	 * @param number the given input
	 * @return the floored square number base
	 */
	private static int lessThanHundredSquareBase(int number) {
		for (int i = 1; i < SMALL_SQUARE_PAIRS.length; ++i) {
			if (SMALL_SQUARE_PAIRS[i][1] > number) {
				return SMALL_SQUARE_PAIRS[i - 1][0];
			}
		}
		return SMALL_SQUARE_PAIRS[SMALL_SQUARE_PAIRS.length - 1][0];
	}
	
	/**
	 * TODO: write comments
	 * @param bitlength
	 * @return
	 */
	public static ArrayList<BigInteger> generateRSAData(int bitlength, int bitEpsHalf) {
		ArrayList<BigInteger> pq = generateRSAPrimes(bitlength, bitEpsHalf);
		BigInteger q = pq.get(0);
		BigInteger p = pq.get(1);
		BigInteger n = p.multiply(q);
		BigInteger phi = p.subtract(ONE).multiply(q.subtract(ONE));
		BigInteger e = new BigInteger("3");
		BigInteger d = euklidInverse(phi, e);
		while (e.multiply(d).mod(phi).compareTo(ONE) != 0) {
			e = e.nextProbablePrime();
			d = euklidInverse(phi, e);
		}
		ArrayList<BigInteger> result = new ArrayList<BigInteger>();
		result.add(n);
		result.add(e);
		result.add(q);
		result.add(p);
		result.add(phi);
		result.add(d);
		return result;
	}
	
	public static BigInteger encryptRSA(BigInteger n, BigInteger e, BigInteger m) {
		return m.modPow(e, n);
	}
	
	/**
	 * TODO: write comments
	 * @param bitlength
	 * @param bitEpsHalf
	 * @return
	 */
	public static ArrayList<BigInteger> generateRSAPrimes(int bitlength, int bitEpsHalf) {
		ArrayList<BigInteger> primes = new ArrayList<BigInteger>();
		primes.add(BigInteger.probablePrime(bitlength / 2 - bitEpsHalf, new Random()));
		primes.add(BigInteger.probablePrime(bitlength / 2 + (bitlength % 2 == 0 ? 0 : 1) + bitEpsHalf, new Random()));
		return primes;
	}
	
	/**
	 * TODO write comments
	 * @param n
	 * @param e
	 * @return
	 */
	public static BigInteger getRSADecoder(BigInteger n, BigInteger e) {
		// TODO start Thread to do normal FACTORING function (or others) in parallel
		ArrayList<BigInteger> fermatFactors = fermatFactors(n);
		BigInteger q = fermatFactors.get(0);
		BigInteger p = fermatFactors.get(1);
		BigInteger phi = p.subtract(ONE).multiply(q.subtract(ONE));
		return euklidInverse(phi, e);
	}
	
	/**
	 * TODO write comments
	 * @param n
	 * @param e
	 * @param c
	 * @return
	 */
	public static BigInteger hackRSA(BigInteger n, BigInteger e, BigInteger c) {
		BigInteger d = getRSADecoder(n, e);
		return c.modPow(d, n);
	}
	
	/**
	 * TODO write comments
	 * @param n
	 * @param e
	 * @param c
	 * @return
	 */
	public static BigInteger decryptRSA(BigInteger n, BigInteger d, BigInteger c) {
		return c.modPow(d, n);
	}
	
	/**
	 * TODO: write comments
	 * @param phi
	 * @param a
	 * @return
	 */
	public static BigInteger euklidInverse(BigInteger phi, BigInteger a) {
		return euklid(phi, a).get(3).mod(phi);
	}

	/**
	 * calculates gcd(a, b) := g == x * a + y * b and returns (g, x, y).
	 * @param a the first BigInteger
	 * @param b the second BigInteger
	 * @return (g, x, a, y, b) with gcd(a, b) := g == x * a + y * b
	 */
	public static ArrayList<BigInteger> euklid(BigInteger a, BigInteger b) {
		// make a >= b
		if (a.compareTo(b) == -1) {
			BigInteger temp = a;
			a = b;
			b = temp;
		}
		BigInteger initialA = a;
		BigInteger initialB = b;
		// calculate gcd, stores euklid-equations
		ArrayList<ArrayList<BigInteger>> equations = new ArrayList<ArrayList<BigInteger>>();
		while (b.compareTo(ONE) >= 0) {
			ArrayList<BigInteger> equation = new ArrayList<BigInteger>();
			equations.add(equation);
			// gcd(a, b) [a/b := (int)(a/b) Rest a%b <=> a - b*(int)(a/b) == a%b]
			// gcd(a, b) [a / b := d Rest r <=> a - b*d = r] == gcd(b, r)
			BigInteger d = a.divide(b);
			BigInteger r = a.mod(b);
			// store equation as A - B * D = R
			equation.add(a);
			equation.add(b);
			equation.add(d);
			equation.add(r);
			a = b;
			b = r;
		}
		BigInteger g = null;
		if (b.compareTo(ZERO) == 0) {
			g = a;
			if (equations.size() == 1) {
				ArrayList<BigInteger> result = new ArrayList<BigInteger>();
				ArrayList<BigInteger> current = equations.get(0);
				result.add(g);
				result.add(ONE);
				result.add(current.get(0));
				result.add(current.get(2).multiply(ZERO.subtract(ONE)).add(initialB.divide(g)));
				result.add(current.get(1));
				return result;
			}
		} else {
			g = ONE;
		}
		ArrayList<BigInteger> result = new ArrayList<BigInteger>();
		result.add(g);
		// calculate (x, y) from g = x * a + y * b
		boolean foundG = false;
		ArrayList<BigInteger> xySol = new ArrayList<BigInteger>();
		for (int i = 0; i < equations.size(); ++i) {
			ArrayList<BigInteger> current = equations.get(equations.size() - i - 1);
			if (!foundG) {
				if (current.get(3).compareTo(g) == 0) {
					foundG = true;
					// store equation as X * A + Y * B ( == G)
					xySol.add(ONE);
					xySol.add(current.get(0));
					xySol.add(current.get(2).multiply(ZERO.subtract(ONE)));
					xySol.add(current.get(1));
					continue;
				} else {
					continue;
				}
			}
			/**
			 * use old equation "xySol" and apply "current" so it
			 * "current":	A_i - B_i * D_i = R_i
			 * "xySol":		X_r * A_r + Y_r * B_r ( == g)
			 * 
			 * example:
			 *   gcd(40, 7)
			 *       | a  | b  | q  | r  // a - b * q = r
			 *   ----+----+----+----+----
			 *   e_0 |  5 |  2 |  2 |  1
			 *   e_1 |  7 |  5 |  1 |  2
			 *   e_2 | 40 |  7 |  5 |  5
			 *   
			 *       | x  | a  | y  | b  | g  // x * a + y * b = g
			 *   ----+----+----+----+----+----
			 *   r_0 |  1 |  5 | -2 |  2 |  g
			 *   r_1 | -2 |  7 |  3 |  5 |  g
			 *   r_2 |  3 | 40 |-17 |  7 |  g
			 *        ####      ####      ####
			 *   => return ArrayList(g, x, y);
			 */
			// apply the next equation to the solution at construction
			ArrayList<BigInteger> xyNext = new ArrayList<BigInteger>();
			xyNext.add(xySol.get(2));
			xyNext.add(current.get(0));
			xyNext.add(xySol.get(2).multiply(current.get(2)).multiply(ZERO.subtract(ONE)).add(xySol.get(0)));
			xyNext.add(xySol.get(1));
			xySol = xyNext;
		}
		result.add(xySol.get(0));
		result.add(initialA);
		result.add(xySol.get(2));
		result.add(initialB);
		return result;
	}
	
}
