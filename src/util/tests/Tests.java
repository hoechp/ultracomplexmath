package util.tests;

import java.util.Formatter;
import java.util.Locale;

import util.hypercomplex.Hypercomplex;

public class Tests {

	/**
	 * the number of tests per MULTITEST session.
	 */
	final static int MULTITEST_COUNT = 100;
	/**
	 * The number of ciphers behind the floating point that are to check.
	 */
	final static int CHECK_COUNT = 10;
	/**
	 * The tolerance of how much two value can differ and still be seen as the same.
	 */
	public final static double DELTA = Math.pow(10, -CHECK_COUNT); // 1e-CHECK_COUNT
	
	public static int countString(String outer, String inner) {
		int count = 0;
		for (int i = 0; i < outer.length(); ++i) {
			int pos = outer.indexOf(inner, i);
			if (pos >= 0) {
				++count;
				i += inner.length() - 1;
			}
		}
		return count;
	}
	
	public static String doubleWithFactorToString(Double value, String factor, boolean signed) {
		if (value == null) {
			return null;
		}
		if (Math.abs(value) < Tests.DELTA) {
			return "0";
		}
		boolean isInt = false;
		boolean isSign = false;
		if (Math.abs(value - value.intValue()) < Tests.DELTA) {
			isInt = true;
			if (value.intValue() == 1 || value.intValue() == -1) {
				isSign = true;
			}
		}
		String result = "";
		if (signed) {
			if (value >= 0) {
				result = "+";
			}
		}
		if (isSign) {
			if (factor == null) {
				result += value.intValue();
			} else {
				result += (value.intValue() < 0 ? "-" : "") + factor;
			}
			return result;
		}
		if (isInt) {
			if (factor == null) {
				result += value.intValue();
			} else {
				result += value.intValue() + factor;
			}
			return result;
		}
		StringBuilder sb = new StringBuilder();
		Formatter formatter = new Formatter(sb);
		String format = "";
		if (!signed) {
			format = "%." + (Hypercomplex.DISPLAYED_CIPHER_COUNT) + "f"; // g = general, d = decimal, e = scientific, + = sign, ( = ()
		} else {
			format = "%+." + (Hypercomplex.DISPLAYED_CIPHER_COUNT) + "f";
		}
		formatter.format(Locale.ENGLISH, format, value);
		formatter.close();
		String rawNumber = sb.toString();
		while (rawNumber.endsWith("0")) {
			rawNumber = rawNumber.substring(0, rawNumber.length() - 1);
		}
		if (rawNumber.endsWith(".")) {
			rawNumber = rawNumber.substring(0, rawNumber.length() - 1);
		}
		if (factor == null) {
			return rawNumber;
		} else {
			return rawNumber + factor;
		}
	}
	
	/**
	 * Compares the provided values per checking if the absolute of the quotient of the values minus one exceeds a constant DELTA value.
	 * If one values is zero it is merely checked if the absolute of the other value exceeds DELTA.
	 * @param expected the expected value (or just value a)
	 * @param actual the actual value (or just value b)
	 * @return true if the values are practically the same otherwise false
	 */
	public static boolean compareValue(double expected, double actual) {
		return compareValue(expected, actual, 1);
	}
	
	/**
	 * Compares the provided values per checking if the absolute of the quotient of the values minus one exceeds a constant DELTA value.
	 * If one values is zero it is merely checked if the absolute of the other value exceeds DELTA.
	 * @param expected the expected value (or just value a)
	 * @param actual the actual value (or just value b)
	 * @return true if the values are practically the same otherwise false
	 */
	public static boolean compareValue(double expected, double actual, double inaccuracy) {
		if (expected == 0) {
			if (actual == 0) {
				return true;
			} else {
				return Math.abs(actual) < DELTA * inaccuracy;
			}
		}
		if (actual == 0) {
			if (expected == 0) {
				return true;
			} else {
				return Math.abs(expected) < DELTA * inaccuracy;
			}
		}
		if (Math.abs(expected) < DELTA * inaccuracy / 2 && Math.abs(actual) < DELTA * inaccuracy / 2) {
			return true;
		}
		double factor = Math.max(expected / actual, actual / expected);
		return factor >= 1 && factor - 1 < DELTA * inaccuracy;
	}
	
}
