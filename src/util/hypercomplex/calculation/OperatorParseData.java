package util.hypercomplex.calculation;

import util.hypercomplex.ultracomplex.Ultra;

public class OperatorParseData {

	private Operator[] operators;
	private String[] strings;
	private Ultra value;
	
	public OperatorParseData(Operator[] operators, String[] strings) {
		this.operators = operators;
		this.strings = strings;
		this.value = null;
	}
	
	public OperatorParseData(Ultra value) {
		this.operators = null;
		this.strings = null;
		this.value = value;
	}
	
	public Operator[] getOperators() {
		return operators;
	}
	public String[] getStrings() {
		return strings;
	}
	public Ultra getValue() {
		return value;
	}
	
}
