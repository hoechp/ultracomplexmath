package util.kd.clustering;

import java.util.HashSet;
import java.util.Vector;

public class Cluster {
	
	private HashSet<Vector<Double>> dataSet;
	
	public Cluster() {
		this(new HashSet<Vector<Double>>());
	}
	
	public Cluster(HashSet<Vector<Double>> dataSet) {
		this.dataSet = dataSet;
	}

	public HashSet<Vector<Double>> getDataSet() {
		return dataSet;
	}

	public void setDataSet(HashSet<Vector<Double>> dataSet) {
		this.dataSet = dataSet;
	}
	
	public Cluster mergedWith(Cluster other) {
		HashSet<Vector<Double>> data = new HashSet<Vector<Double>>();
		data.addAll(this.getDataSet());
		data.addAll(other.getDataSet());
		return new Cluster(data);
	}
	
	public void merge(Cluster other) {
		become(mergedWith(other));
	}
	
	public void become(Cluster other) {
		setDataSet(other.getDataSet());
	}

}
