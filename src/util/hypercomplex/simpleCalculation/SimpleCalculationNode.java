package util.hypercomplex.simpleCalculation;

import java.util.ArrayList;

import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;

public class SimpleCalculationNode {
	
	private boolean constant;
	private Hypercomplex value;
	private SimpleOperator operator;
	private ArrayList<SimpleCalculationNode> children = new ArrayList<SimpleCalculationNode>();

	public SimpleCalculationNode(Hypercomplex value) {
		this.constant = true;
		this.value = value;
		this.operator = null;
	}
	
	public SimpleCalculationNode(SimpleOperator operator) {
		this.constant = false;
		this.value = null;
		this.operator = operator;
	}
	
	private static Hypercomplex sameKind(Hypercomplex reference) {
		return reference.times(0).plus(Complex.ONE);
	}
	
	public Hypercomplex computedResult() {
		return value = internallyComputedResult();
	}
	
	public Hypercomplex internallyComputedResult() {
		if (operator == null || children.size() != operator.involvedTerms()) {
			return null;
		}
		switch (operator.code()) {
		case 0:
			return children.get(0).getValue();
		case 1:
			return children.get(0).getValue().times(children.get(1).getValue());
		case 2:
			return children.get(0).getValue().by(children.get(1).getValue());
		case 3:
			return children.get(0).getValue().plus(children.get(1).getValue());
		case 4:
			return children.get(0).getValue().minus(children.get(1).getValue());
		case 5:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().dot(children.get(1).getValue()));
		case 6:
			// base first
			return children.get(0).getValue().pow(children.get(1).getValue());
		case 7:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().abs());
		case 8:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().det());
		case 9:
			return children.get(0).getValue().exp();
		case 10:
			return children.get(0).getValue().ln();
		case 11:
			// base first
			return children.get(1).getValue().log(children.get(0).getValue());
		case 12:
			return children.get(0).getValue().cos();
		case 13:
			return children.get(0).getValue().acos();
		case 14:
			return children.get(0).getValue().cosh();
		case 15:
			return children.get(0).getValue().acosh();
		case 16:
			return children.get(0).getValue().sin();
		case 17:
			return children.get(0).getValue().asin();
		case 18:
			return children.get(0).getValue().sinh();
		case 19:
			return children.get(0).getValue().asinh();
		case 20:
			return children.get(0).getValue().tan();
		case 21:
			return children.get(0).getValue().atan();
		case 22:
			return children.get(0).getValue().tanh();
		case 23:
			return children.get(0).getValue().atanh();
		case 24:
			return children.get(0).getValue().cot();
		case 25:
			return children.get(0).getValue().acot();
		case 26:
			return children.get(0).getValue().coth();
		case 27:
			return children.get(0).getValue().acoth();
		case 28:
			return children.get(0).getValue().sec();
		case 29:
			return children.get(0).getValue().asec();
		case 30:
			return children.get(0).getValue().sech();
		case 31:
			return children.get(0).getValue().asech();
		case 32:
			return children.get(0).getValue().csc();
		case 33:
			return children.get(0).getValue().acsc();
		case 34:
			return children.get(0).getValue().csch();
		case 35:
			return children.get(0).getValue().acsch();
		case 36:
			return children.get(0).getValue().pow(0.5);
		case 37:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().angle());
		case 38:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().length());
		case 39:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().eulerAngle());
		case 40:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().eulerLength());
		case 41:
			return children.get(0).getValue().conjugate();
		case 42:
			return children.get(0).getValue().inverse();
		case 43:
			return children.get(0).getValue().r0();
		case 44:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().re());
		case 45:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().im());
		case 46:
			return children.get(0).getValue().mirroredRadialTo(children.get(1).getValue());
		case 47:
			return children.get(0).getValue().mirroredOrthogonalTo(children.get(1).getValue());
		case 48:
			return children.get(0).getValue().partInDirection(children.get(1).getValue());
		case 49:
			return children.get(0).getValue().partOrthogonallyTo(children.get(1).getValue());
		case 50:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().round());
		case 51:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().ceil());
		case 52:
			return sameKind(children.get(0).getValue()).times(
					children.get(0).getValue().floor());
		case 53:
			return children.get(0).getValue().times(children.get(0).getValue());
		case 54:
			return children.get(0).getValue().times(children.get(0).getValue()).times(children.get(0).getValue());
		case 55:
			return children.get(0).getValue().times(-1);
		default:
			return null;
		}
	}
	
	public ArrayList<SimpleCalculationNode> getChildren() {
		return children;
	}
	public void addChild(SimpleCalculationNode child) {
		children.add(child);
	}
	public boolean isConstant() {
		return constant;
	}
	public Hypercomplex getValue() {
		if (value != null) {
			return value;
		} else {
			return computedResult();
		}
	}
	public SimpleOperator getOperator() {
		return operator;
	}
	
	@Override
	public String toString() {
		return toString(false, true);
	}
	
	public String toString(boolean showOuterBracktets, boolean showInnerBracktets) {
		if (constant) {
			return value.toString();
		}
		final int n = operator.involvedTerms();
		if (n == 1) {
			if (getOperator() != SimpleOperator.BRACKETS && children.get(0).getOperator() != SimpleOperator.BRACKETS) {
				return operator.leftSymbol()
						+ (!showInnerBracktets ? "" : SimpleOperator.BRACKETS.leftSymbol())
						+ children.get(0).toString(showOuterBracktets, showInnerBracktets)
						+ (!showInnerBracktets ? "" : SimpleOperator.BRACKETS.rightSymbol())
						+ operator.rightSymbol();
			}
			return operator.leftSymbol()
					+ children.get(0).toString(showOuterBracktets, showInnerBracktets)
					+ operator.rightSymbol();
		} else if (n == 2) {
			boolean zeroMinusX = SimpleOperator.MINUS == operator && children.get(0).toString().equals("0");
			boolean zeroPlus = SimpleOperator.PLUS == operator && children.get(0).toString().equals("0");
			boolean zeroPlusMinusX = zeroMinusX || zeroPlus;
			return  (!showOuterBracktets ? "" : SimpleOperator.BRACKETS.leftSymbol())
					+ operator.leftSymbol()
					+ (zeroPlusMinusX ? "" : children.get(0).toString(showOuterBracktets, showInnerBracktets))
					+ (zeroPlus ? "" : operator.middleSymbol())
					+ children.get(1).toString(showOuterBracktets, showInnerBracktets)
					+ operator.rightSymbol()
					+ (!showOuterBracktets ? "" : SimpleOperator.BRACKETS.rightSymbol());
		} else {
			System.err.println("DESIGN ERROR DUE TO NEW TYPE OPERATORS! REDESIGN NEEDED!");
			return "UNPRINTABLE EXPRESSION DUE TO NEW TYPE OPERATORS! REDESIGN NEEDED!";
		}
	}
	
}
