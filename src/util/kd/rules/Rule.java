package util.kd.rules;

import java.util.HashSet;

public class Rule {
	
	private Data origin;
	
	private DataSet a;
	private DataSet b;
	private HashSet<DataSet> cut;
	private HashSet<DataSet> union;
	
	public Rule(DataSet a, DataSet b) {
		this.a = a;
		this.b = b;
		origin = a.getOrigin();
		cut = cut(a.getSupp(), b.getSupp());
		union = union(a.getSupp(), b.getSupp());
	}
	
	public DataSet getA() {
		return a;
	}
	public DataSet getB() {
		return b;
	}

	public double conf() {
		return (double)cut.size() / (double)a.getSupp().size();
	}
	
	public double supp() {
		return (double)union.size() / (double)origin.size();
	}
	
	public static HashSet<DataSet> cut(HashSet<DataSet> a, HashSet<DataSet> b) {
		HashSet<DataSet> result = new HashSet<DataSet>();
		for (DataSet d: a) {
			if (b.contains(d)) {
				result.add(d);
			}
		}
		return result;
	}
	
	public static HashSet<DataSet> union(HashSet<DataSet> a, HashSet<DataSet> b) {
		HashSet<DataSet> result = new HashSet<DataSet>();
		for (DataSet d: a) {
			result.add(d);
		}
		for (DataSet d: b) {
			result.add(d);
		}
		return result;
	}
	
	public String toString() {
		return "r_(" + a.getDataList() + " -> " + b.getDataList() + ")";
	}
	
}
