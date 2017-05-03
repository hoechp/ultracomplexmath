package util.hypercomplex.simpleCalculation;

import util.hypercomplex.Hypercomplex;

public class SimpleOperatorParseData {

	private SimpleOperator[] operators;
	private String[] strings;
	private Hypercomplex value;
	
	public SimpleOperatorParseData(SimpleOperator[] operators, String[] strings) {
		this.operators = operators;
		this.strings = strings;
		this.value = null;
	}
	
	public SimpleOperatorParseData(Hypercomplex value) {
		this.operators = null;
		this.strings = null;
		this.value = value;
	}
	
	public SimpleOperator[] getOperators() {
		return operators;
	}
	public String[] getStrings() {
		return strings;
	}
	public Hypercomplex getValue() {
		return value;
	}
	
}
