package util.hypercomplex.mechanism;

import java.util.HashMap;

public class Machine {
	
	private HashMap<String, Actor> map = new HashMap<String, Actor>();
	private HashMap<String, Mechanism> mechanismMap = new HashMap<String, Mechanism>();
	
	public Machine(Mechanism root) {
		mechanismMap.put("root", root);
	}
	
	public void connect(String newMech, String oldMech) {
		mechanismMap.put(newMech, new Mechanism(mechanismMap.get(oldMech)));
	}
	
	public Mechanism get(String key) {
		return mechanismMap.get(key);
	}
	
	public HashMap<String, Actor> actors() {
		return map;
	}
	
	public HashMap<String, Mechanism> mechanisms() {
		return mechanismMap;
	}

}
