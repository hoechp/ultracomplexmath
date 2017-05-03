package util.kd.clustering;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Vector;


public class HierarchicalCluster extends Cluster {

	private HierarchicalCluster leftSide;
	private HierarchicalCluster rightSide;
	private boolean leaf;
	private int key;
	
	public int getKey() {
		return key;
	}

	public void setKey(int k) {
		this.key = k;
	}
	
	public HierarchicalCluster() {
		this(new HashSet<Vector<Double>>());
		key = -1;
	}
	
	public HierarchicalCluster(HashSet<Vector<Double>> dataSet) {
		key = -1;
		setDataSet(dataSet);
		leftSide = null;
		rightSide = null;
		leaf = true;
	}
	
	public HierarchicalCluster(HierarchicalCluster left, HierarchicalCluster right) {
		HashSet<Vector<Double>> data = new HashSet<Vector<Double>>();
		data.addAll(left.getDataSet());
		data.addAll(right.getDataSet());
		setDataSet(data);
		leftSide = left;
		rightSide = right;
		leaf = false;
	}
	
	public HierarchicalCluster mergedWith(HierarchicalCluster other) {
		HierarchicalCluster thisCp = new HierarchicalCluster();
		thisCp.become(this);
		return new HierarchicalCluster(thisCp, other);
	}
	
	public void merge(HierarchicalCluster other) {
		become(mergedWith(other));
	}
	
	public void become(HierarchicalCluster other) {
		setDataSet(other.getDataSet());
		setLeaf(other.isLeaf());
		setLeftSide(other.getLeftSide());
		setRightSide(other.getRightSide());
		setKey(other.getKey());
	}
	
	public HierarchicalCluster getLeftSide() {
		return leftSide;
	}

	public void setLeftSide(HierarchicalCluster leftSide) {
		this.leftSide = leftSide;
	}

	public HierarchicalCluster getRightSide() {
		return rightSide;
	}

	public void setRightSide(HierarchicalCluster rightSide) {
		this.rightSide = rightSide;
	}

	public boolean isLeaf() {
		return leaf;
	}

	public void setLeaf(boolean leaf) {
		this.leaf = leaf;
	}
	
	public HashSet<Cluster> toCluster(int count) {
		/**
		 * until size reached: split node with highest key into two
		 * -> by dividing the part off that has the highest key 
		 */
		ArrayList<HierarchicalCluster> collection = new ArrayList<HierarchicalCluster>();
		collection.add(this);
		int extra = 0;
		while (collection.size() < count + extra) {
			// find non-split node with highest key
			int highestKey = -1;
			int index = -1;
			for (int i = 0; i < collection.size(); ++i) {
				int key = collection.get(i).getKey();
				if (key > highestKey) {
					highestKey = key;
					index = i;
				}
			}
			if (index == -1) {
				break;
			}
			HierarchicalCluster winner = collection.get(index);
			collection.add(winner.getRightSide());
			if (winner.getRightSide().getDataSet().size() == 0) {
				++extra;
			}
			winner.become(winner.getLeftSide());
		}
		// copy as HashSet of normal Clusters and return
		HashSet<Cluster> result = new HashSet<Cluster>();
		for (HierarchicalCluster c: collection) {
			result.add(new Cluster(c.getDataSet()));
		}
		return result;
	}

	public static HashSet<Cluster> hierarchicalClusterSetToClusterSet(HashSet<HierarchicalCluster> c) {
		HashSet<Cluster> result = new HashSet<Cluster>();
		for (HierarchicalCluster cl: c) {
			result.add(cl);
		}
		return result;
	}
	
	public String toString() {
		return getDataSet().size() + " points";
	}

}
