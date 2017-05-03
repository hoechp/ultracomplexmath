package util.kd.terms;

import java.util.HashSet;

public class Thing {
	
	private HashSet<Property> properties;
	
	public Thing(HashSet<Property> properties) {
		this.properties = properties;
	}
	
	public HashSet<Property> getProperties() {
		return properties;
	}
	
	public String toString() {
		return "d_" + properties.toString();
	}

}
