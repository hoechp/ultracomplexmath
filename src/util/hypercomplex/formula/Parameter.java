package util.hypercomplex.formula;

import util.hypercomplex.calculation.Calculation;
import util.hypercomplex.ultracomplex.Ultra;

public class Parameter {

	private String identifier;
	private Formula formula;

	public Parameter(String identifier, Ultra value) {
		this.identifier = identifier;
		setValue(value);
	}
	public Parameter(String identifier, Calculation calc) {
		this.identifier = identifier;
		setCalculation(calc);
	}
	public Parameter(String identifier, Formula formula) {
		this.identifier = identifier;
		setFormula(formula);
	}

	public String getIdentifier() {
		return identifier;
	}
	public Ultra getValue() {
		return formula.result();
	}
	public Formula getFormula() {
		return formula;
	}
	public void setFormula(Formula formula) {
		this.formula = formula;
	}
	public void setCalculation(Calculation calc) {
		this.formula = new Formula(calc);
	}
	public void setValue(Ultra value) {
		this.formula = new Formula(value);
	}
	
	@Override
	public String toString() {
		String result = formula.toString();
		if (formula.getParameter().size() > 0) {
			result = "(" + result + ")";
		}
		return identifier + " = " + result;
	}
	
}
