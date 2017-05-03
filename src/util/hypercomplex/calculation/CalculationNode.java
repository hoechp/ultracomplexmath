package util.hypercomplex.calculation;

import java.util.ArrayList;

import util.hypercomplex.ultracomplex.Ultra;

public class CalculationNode {
	
	private boolean constant;
	private Ultra value;
	private Operator operator;
	private ArrayList<CalculationNode> children = new ArrayList<CalculationNode>();

	public CalculationNode(Ultra value) {
		this.constant = true;
		this.value = value;
		this.operator = null;
	}
	
	public CalculationNode(Operator operator) {
		this.constant = false;
		this.value = null;
		this.operator = operator;
	}
	
	public Ultra computedResult() {
		return value = internallyComputedResult();
	}
	
	public Ultra internallyComputedResult() {
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
		case 6:
			// base first
			return children.get(0).getValue().pow(children.get(1).getValue());
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
			return children.get(0).getValue().pow(new Ultra(0.5));
		case 41:
			return children.get(0).getValue().conjugate();
		case 42:
			return children.get(0).getValue().inverse();
		case 44:
			return new Ultra(children.get(0).getValue().getDouble(0));
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
	
	public ArrayList<CalculationNode> getChildren() {
		return children;
	}
	public void addChild(CalculationNode child) {
		children.add(child);
	}
	public boolean isConstant() {
		return constant;
	}
	public Ultra getValue() {
		if (value != null) {
			return value;
		} else {
			return computedResult();
		}
	}
	public Operator getOperator() {
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
			if (getOperator() != Operator.BRACKETS && children.get(0).getOperator() != Operator.BRACKETS) {
				return operator.leftSymbol()
						+ (!showInnerBracktets ? "" : Operator.BRACKETS.leftSymbol())
						+ children.get(0).toString(showOuterBracktets, showInnerBracktets)
						+ (!showInnerBracktets ? "" : Operator.BRACKETS.rightSymbol())
						+ operator.rightSymbol();
			}
			return operator.leftSymbol()
					+ children.get(0).toString(showOuterBracktets, showInnerBracktets)
					+ operator.rightSymbol();
		} else if (n == 2) {
			boolean zeroMinusX = Operator.MINUS == operator && children.get(0).toString().equals("0");
			boolean zeroPlus = Operator.PLUS == operator && children.get(0).toString().equals("0");
			boolean zeroPlusMinusX = zeroMinusX || zeroPlus;
			return  (!showOuterBracktets ? "" : Operator.BRACKETS.leftSymbol())
					+ operator.leftSymbol()
					+ (zeroPlusMinusX ? "" : children.get(0).toString(showOuterBracktets, showInnerBracktets))
					+ (zeroPlus ? "" : operator.middleSymbol())
					+ children.get(1).toString(showOuterBracktets, showInnerBracktets)
					+ operator.rightSymbol()
					+ (!showOuterBracktets ? "" : Operator.BRACKETS.rightSymbol());
		} else {
			System.err.println("DESIGN ERROR DUE TO NEW TYPE OPERATORS! REDESIGN NEEDED!");
			return "UNPRINTABLE EXPRESSION DUE TO NEW TYPE OPERATORS! REDESIGN NEEDED!";
		}
	}
	
}
