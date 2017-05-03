package util.kd.rules;

import java.util.ArrayList;
import java.util.HashSet;

public class RuleDeduction {
	
	/**
	 * rule deduction with data sets ("transactions")
	 * - HashSet<DataSet> apriori(double minSupp)
	 * - double supp(DataSet d)
	 * - HashSet<Rule> ruleGeneration(HashSet<DataSet> d)
	 * - double conf(Rule)
	 * - double supp(Rule)
	 * (...)
	 */
	
	private Data data;
	private HashSet<Integer> total;
	private HashSet<DataSet> items;
	private HashSet<Rule> rules;
	
	public RuleDeduction(Data data, double itemMinSupp, double ruleMinConf, double ruleMinSupp) {
		this.data = data;
		total = new HashSet<Integer>();
		items = new HashSet<DataSet>();
		rules = new HashSet<Rule>();
		scanTotal();
		apriori(itemMinSupp);
		makeRules();
		filterRules(ruleMinConf, ruleMinSupp);
	}

	private void scanTotal() {
		for (DataSet d: data.getAllData()) {
			for (int i: d.getDataList()) {
				total.add(i);
			}
		}
	}

	private void apriori(double minSupp) {
		// first add all 1-sized elements
		ArrayList<HashSet<DataSet>> steps = new ArrayList<HashSet<DataSet>>();
		steps.add(new HashSet<DataSet>());
		HashSet<DataSet> step = steps.get(0);
		for (int i: total) {
			HashSet<Integer> set = new HashSet<Integer>();
			set.add(i);
			step.add(new DataSet(data, set));
		}
		HashSet<DataSet> nextStep = null;
		do {
			// then remove those with supp < minSupp
			HashSet<DataSet> toRemove = new HashSet<DataSet>();
			for (DataSet d: step) {
				if (d.supp() <= minSupp) {
					toRemove.add(d);
				}
			}
			step.removeAll(toRemove);
			// then combine to higher-order elements
			nextStep = new HashSet<DataSet>();
			for (DataSet d: step) {
				for (int i: total) {
					if (!d.getDataList().contains(i)) {
						HashSet<Integer> combo = new HashSet<Integer>();
						combo.addAll(d.getDataList());
						combo.add(i);
						boolean doesExist = false;
						for (DataSet d2: nextStep) {
							if (d2.getDataList().containsAll(combo)
									&& combo.containsAll(d2.getDataList())) {
								doesExist = true;
								break;
							}
						}
						if (!doesExist) {
							DataSet newCombo = new DataSet(data, combo);
							nextStep.add(newCombo);
						}
					}
				}
			}
			steps.add(nextStep);
			step = nextStep;
		} while (nextStep.size() > 0);
		// then add all elements to the final result and 'return'
		HashSet<DataSet> result = new HashSet<DataSet>();
		for (HashSet<DataSet> s: steps) {
			for (DataSet d: s) {
				result.add(d);
			}
		}
		items = result;
	}

	public Data getData() {
		return data;
	}

	public HashSet<Integer> getTotal() {
		return total;
	}

	public HashSet<DataSet> getItems() {
		return items;
	}

	public HashSet<Rule> getRules() {
		return rules;
	}

	private void makeRules() {
		HashSet<Rule> result = new HashSet<Rule>();
		for (DataSet a: items) {
iteration:	for (DataSet b: items) {
				if (a != b) {
					for (int i: b.getDataList()) {
						if (a.getDataList().contains(i)) {
							continue iteration;
						}
					}
					result.add(new Rule(a, b));
				}
			}
		}
		rules = result;
	}
	
	private void filterRules(double minConf, double ruleSupp) {
		HashSet<Rule> result = new HashSet<Rule>();
		for (Rule r: rules) {
			if (r.conf() >= minConf && r.supp() > ruleSupp) {
				result.add(r);
			}
		}
		rules = result;
	}
	
}
