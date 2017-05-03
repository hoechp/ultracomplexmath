package util.kd.terms;

import java.util.HashSet;

import util.kd.rules.Data;

public class Things {
	
	private HashSet<Property> usedProperties;
	private HashSet<Thing> things;
	
	public HashSet<Property> getUsedProperties() {
		return usedProperties;
	}

	public HashSet<Thing> getThings() {
		return things;
	}

	public Things(HashSet<Thing> things) {
		this(properties(things), things);
	}
	
	public Property property(int code) {
		for (Property p: usedProperties) {
			if (p.getId() == code) {
				return p;
			}
		}
		return null;
	}
	
	public Data toData() {
		Data data = new Data();
		for (Thing t: things) {
			HashSet<Integer> propertyCodes = new HashSet<Integer>();
			for (Property p: t.getProperties()) {
				propertyCodes.add(p.getId());
			}
			data.addData(propertyCodes);
		}
		return data;
	}

	private static HashSet<Property> properties(HashSet<Thing> things) {
		HashSet<Property> properties = new HashSet<Property>();
		for (Thing g: things) {
			for (Property e: g.getProperties()) {
				properties.add(e);
			}
		}
		return properties;
	}
	
	public Things(HashSet<Property> properties, HashSet<Thing> things) {
		usedProperties = properties;
		this.things = things;
	}
	
	/**
	 * RANDOM // TODO
	 * @param eigenschaften
	 * @param gegenstaende
	 * @param minSupp
	 */
	public Things(int propertyCount, int charCount, int thingCount, double chance) {
		usedProperties = new HashSet<Property>();
		for (int i = 0; i < propertyCount; ++i) {
			String randomName = null;
			boolean redo = true;
			while (redo) {
				redo = false;
				randomName = randomString(charCount);
				for (Property p: usedProperties) {
					if (p.getName().equals(randomName)) {
						redo = true;
					}
				}
			}
			usedProperties.add(new Property(randomName, i));
		}
		this.things = new HashSet<Thing>();
		for (int i = 0; i < thingCount; ++i) {
			HashSet<Property> properties = new HashSet<Property>();
			for (Property e: usedProperties) {
				if (Math.random() < chance) {
					properties.add(e);
				}
			}
			this.things.add(new Thing(properties));
		}
	}

	private String randomString(int length) {
		char from = '?';
		char to = '?';
		String randomName = "";
		for (int j = 0; j < length; ++j) {
			if (Math.random() < 0.5) {
				from = 'a';
				to = 'z';
			} else {
				from = 'A';
				to = 'Z';
			}
			char toAdd = (char)((int)from + ((int)to - (int)from) * Math.random());
			randomName = randomName + toAdd;
		}
		return randomName;
	}
	
}
