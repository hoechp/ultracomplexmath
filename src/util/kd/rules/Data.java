package util.kd.rules;

import java.util.HashSet;

public class Data {
	
	private HashSet<DataSet> allData;

	public Data() {
		allData = new HashSet<DataSet>();
	}
	
	public void init() {
		for (DataSet d: allData) {
			d.init();
		}
	}
	
	public void addData(HashSet<Integer> d) {
		allData.add(new DataSet(this, d, false));
	}

	public HashSet<DataSet> getAllData() {
		return allData;
	}

	public void setAllData(HashSet<DataSet> allData) {
		this.allData = allData;
	}
	
	public int size() {
		return allData.size();
	}

}
