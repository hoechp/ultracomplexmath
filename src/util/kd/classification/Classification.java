package util.kd.classification;

import java.util.ArrayList;

public class Classification {
	
	ArrayList<ArrayList<Boolean>> data;
	
	void initRandom(int columns, int rows) {
		data = new ArrayList<ArrayList<Boolean>>();
		for (int i = 0; i < columns; ++i) {
			data.add(new ArrayList<Boolean>());
			for (int j = 0; j < rows; ++j) {
				if (Math.random() < 0.5) {
					data.get(i).add(true);
				} else {
					data.get(i).add(false);
				}
			}
		}
	}
	
	/**
	 * 1. you could use a function to take the column (except the one to classify) that has the biggest
	 * positive or negative correspondence to the value to classify.
	 * 
	 * 2. if the positive indication is bigger, classify positive if the flag is positive. if the negative
	 * indication is stronger, classify if the flag is negative. in the other case though,
	 * look for the second-strongest positive or negative indicating column
	 * 
	 * 3. continue with the selected column like in 2. or end if classified.
	 * 
	 * TODO: implement or implement better strategy from KDD class
	 */
	
	ArrayList<ArrayList<Double>> indication(int column) {
		ArrayList<ArrayList<Double>> result = new ArrayList<ArrayList<Double>>();
		result.add(new ArrayList<Double>());
		result.add(new ArrayList<Double>());
		for (int i = 0; i < data.size(); ++i) {
			int truthCount = 0;
			double sumTrue = 0;
			double sumFalse = 0;
			for (int j = 0; j < data.get(column).size(); ++j) {
				if (data.get(i).get(j)) {
					++truthCount;
					if (data.get(column).get(j)) {
						sumTrue += 1;
					}
				} else {
					if (data.get(column).get(j)) {
						sumFalse += 1;
					}
				}
			}
			result.get(0).add(sumTrue / truthCount);
			result.get(1).add(sumFalse / (data.get(column).size() - truthCount));
		}
		return result;
	}

}
