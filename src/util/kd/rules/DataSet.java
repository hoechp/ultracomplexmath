package util.kd.rules;

import java.util.HashSet;

public class DataSet {
	
	private Data origin;
	private HashSet<Integer> dataList;
	private HashSet<DataSet> supp = null;
	
	public HashSet<DataSet> getSupp() {
		return supp;
	}
	
	public DataSet(Data o, HashSet<Integer> d) {
		this(o, d, true);
	}

	public DataSet(Data o, HashSet<Integer> d, boolean init) {
		origin = o;
		dataList = d;
		if (init) {
			init();
		}
	}
	
	public Data getOrigin() {
		return origin;
	}

	
	public HashSet<Integer> getDataList() {
		return dataList;
	}
	
	public void init() {
		supp = new HashSet<DataSet>();
		for (DataSet d: origin.getAllData()) {
			if (d.getDataList().containsAll(dataList)) {
				supp.add(d);
			}
		}
	}
	
	double supp() {
		return (double)supp.size() / (double)origin.size();
	}
	
	public String toString() {
		return "d_" + dataList.toString();
	}
	
}
