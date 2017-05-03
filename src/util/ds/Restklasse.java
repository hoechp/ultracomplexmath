package util.ds;

import java.util.HashSet;

public class Restklasse {

	private ZModuloNZRing owningSet;
	private int value;
	private int n;
	
	public Restklasse(ZModuloNZRing owningSet, int value) {
		this.owningSet = owningSet;
		this.value = value;
		this.n = owningSet.getN();
	}

	public Restklasse plus(Restklasse other) {
		int rawVal = this.getValue() + other.getValue();
		return this.getOwningSet().getRestklassen().get(rawVal % this.getOwningSet().getN());
	}
	
	public Restklasse mal(Restklasse other) {
		int rawVal = this.getValue() * other.getValue();
		return this.getOwningSet().getRestklassen().get(rawVal % this.getOwningSet().getN());
	}
	
	public HashSet<Restklasse> eckig() {
		HashSet<Restklasse> result = new HashSet<Restklasse>();
		int val = 1;
		for (int j = 0; j < n; ++j) {
			result.add(owningSet.getRestklassen().get(val));
			val *= value;
			val %= n;
		}
		return result;
	}
	
	public int ord() {
		return eckig().size();
	}
	
	public int getValue() {
		return value;
	}
	
	public ZModuloNZRing getOwningSet() {
		return owningSet;
	}
	
	@Override
	public String toString() {
		/* *
		int add = (int)(Math.log10(getOwningSet().getN() - 1)) - (int)(Math.log10(value));
		if (value == 0) {
			add = (int)(Math.log10(getOwningSet().getN() - 1)) - (int)(Math.log10(value + 1));
		}
		/* */
		StringBuffer buf = new StringBuffer();
		/* *
		for (int i = 0; i < add; ++i) {
			buf.append(" ");
		}
		/* */
		buf.append("[");
		buf.append(value);
		buf.append("]_" + getOwningSet().getN());
		//buf.append("]");
		return buf.toString();
	}
	
}
