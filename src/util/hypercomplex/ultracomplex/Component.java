package util.hypercomplex.ultracomplex;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Hypercomplex;
import util.tests.Tests;

/**
 * types:<br>
 * -1 == ZERO<br>
 * 0 == REAL<br>
 * 1 == Binary<br>
 * 2 == Complex<br>
 * 3 == Complex * Binary<br>
 * 4 == Dual<br>
 * 5 == Dual * Binary<br>
 * 6 == Dual * Complex<br>
 * 7 == Dual * Complex * Binary<br>
 * @author hoechp
 *
 */

public class Component {

	public Component(int type, double value) {
		this.type = type;
		setValue(hyperType(type, value));
	}
	
	public Component(int type, Hypercomplex value) {
		this.type = type;
		setValue(value);
	}
	
	public int getType() {
		return type;
	}
	
	public void setType(int type) {
		this.type = type;
	}

	public Hypercomplex getValue() {
		return value;
	}

	public void setValue(Hypercomplex value) {
		this.value = value;
	}

	static private int[][] multiplicationArr = {
			{+0, +1, +2, +3, +4, +5, +6, +7},
			{+1, +0, +3, +2, +5, +4, +7, +6},
			{+2, +3, +0, +1, +6, +7, +4, +5},
			{+3, +2, +1, +0, +7, +6, +5, +4},
			{+4, +5, +6, +7, -1, -1, -1, -1},
			{+5, +4, +7, +6, -1, -1, -1, -1},
			{+6, +7, +4, +5, -1, -1, -1, -1},
			{+7, +6, +5, +4, -1, -1, -1, -1}
			};
	
	static private int[][] signArr = {
			{0, 0, 0, 0, 0, 0, 0, 0},
			{0, 0, 0, 0, 0, 0, 0, 0},
			{0, 0, 1, 1, 0, 0, 1, 1},
			{0, 0, 1, 1, 0, 0, 1, 1},
			{0, 0, 0, 0, 0, 0, 0, 0},
			{0, 0, 0, 0, 0, 0, 0, 0},
			{0, 0, 1, 1, 0, 0, 0, 0},
			{0, 0, 1, 1, 0, 0, 0, 0}
			};
	
	private int type;
	private Hypercomplex value;

	public Hypercomplex hyperType(int code, double value) {
		switch (code) {
		case -1:
			return new Complex(0, 0);
		case 0:
			return new Complex(value, 0);
		case 1:
			return new Binary(0, value);
		case 2:
			return new Complex(0, value);
		case 3:
			return new Complex(0, value);
		case 4:
			return new Dual(0, value);
		case 5:
			return new Dual(0, value);
		case 6:
			return new Dual(0, value);
		case 7:
			return new Dual(0, value);
		default:
			return null;	
		}
	}
	
	public int multiplicationCode(int a, int b) {
		return multiplicationArr[a][b];
	}
	
	public int signCode(int a, int b) {
		return signArr[a][b];
	}
	
	public Component times(Ultra newOwner, Component other) {
		int code = multiplicationCode(getType(), other.getType());
		int componentCode = code;
		if (componentCode < 0) {
			componentCode = 0;
		}
		int sign = signCode(getType(), other.getType());
		double a = getType() > 0 ? getValue().im() : getValue().re();
		double b = other.getType() > 0 ? other.getValue().im() : other.getValue().re();
		return new Component(componentCode, hyperType(code, Math.pow(-1, sign) * a * b));
	}
	
	@Override
	public String toString() {
		return toStringSimple(false);
	}

	public String toStringSimple(boolean signed) {
		String a = Tests.doubleWithFactorToString(getValue().getCartesian().get(0), "", signed);
		String b = Tests.doubleWithFactorToString(getValue().getCartesian().get(1), "", signed);
		switch (type) {
		case -1:
			return "0";
		case 0:
			return a;
		case 1:
			return b + Binary.I;
		case 2:
			return b + Complex.I;
		case 3:
			return b + Complex.I + Binary.I;
		case 4:
			return b + Dual.I;
		case 5:
			return b + Dual.I + Binary.I;
		case 6:
			return b + Dual.I + Complex.I;
		case 7:
			return b + Dual.I + Complex.I + Binary.I;
		default:
			return "";	
		}
	}

	@Override
	public boolean equals(Object other) {
		if (other instanceof Component) {
			if (getType() != ((Component)other).getType()) {
				return false;
			} else {
				if (!getValue().equals(((Component)other).getValue())) {
					return false;
				} else {
					return true;
				}
			}
		} else {
			return false;
		}
	}

	public double getDouble() {
		if (getType() > 0) {
			return getValue().im();
		} else {
			return getValue().re();
		}
	}

}
