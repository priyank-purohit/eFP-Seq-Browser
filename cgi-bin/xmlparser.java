import java.io.*;
import java.io.File;
import java.io.IOException;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.xml.sax.SAXException;

public class index {
	public static void main(String argv[]) {

		try {
			String filepath = "C:\\Users\\Priyank\\Documents\\PRIYANK\\University of Toronto\\Research\\Provart Lab\\GitHub\\RNA-Browser\\cgi-bin\\data\\bamdata.xml";
			String filepath_out = "C:\\Users\\Priyank\\Documents\\PRIYANK\\University of Toronto\\Research\\Provart Lab\\GitHub\\RNA-Browser\\cgi-bin\\data\\bamdata2.xml";
			DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder docBuilder = docFactory.newDocumentBuilder();
			Document doc = docBuilder.parse(filepath);

			// Get the root element
			Node files = doc.getFirstChild();

			// Get the staff element , it may not working if tag has spaces, or
			// whatever weird characters in front...it's better to use
			// getElementsByTagName() to get it directly.
			// Node staff = company.getFirstChild();

			// Get the staff element by tag name directly
			Node staff = doc.getElementsByTagName("files").item(0);

			// loop the staff child node
			NodeList list = staff.getChildNodes();

			for (int i = 0; i < list.getLength(); i++) {
				Node node = list.item(i);

				if ("file".equals(node.getNodeName())) {

					String pattern = "(http://newland.iplantcollaborative.org/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits.bam)";

					Pattern r = Pattern.compile(pattern);

					Matcher m = r.matcher(node.getAttributes().getNamedItem("name").getNodeValue());

					System.out.println(">>> " + node.getAttributes().getNamedItem("name").getNodeValue());

					String new_lin = "X", ori_exp = "XX";

					if (m.find()) {
						new_lin = new_link(m.group(2));
						//ori_exp = m.group(2);

					}

					// CHANGE >>>>>>>>>>>>>>>>>>>
					node.getAttributes().getNamedItem("name").setTextContent(new_lin);
				}
			}

			// write the content into xml file
			TransformerFactory transformerFactory = TransformerFactory.newInstance();
			Transformer transformer = transformerFactory.newTransformer();
			DOMSource source = new DOMSource(doc);
			StreamResult result = new StreamResult(new File(filepath_out));
			transformer.transform(source, result);

			System.out.println("Done");

		} catch (ParserConfigurationException pce) {
			pce.printStackTrace();
		} catch (TransformerException tfe) {
			tfe.printStackTrace();
		} catch (IOException ioe) {
			ioe.printStackTrace();
		} catch (SAXException sae) {
			sae.printStackTrace();
		}
	}

	public static String new_link(String ori_exp) {
		System.out.println(ori_exp);
		String fileName = "C:\\Users\\Priyank\\Documents\\PRIYANK\\University of Toronto\\Research\\Provart Lab\\GitHub\\RNA-Browser\\cgi-bin\\data\\iplant_path_to_rnaseq_bam_files.txt";

		// This will reference one line at a time
		String line = null, ret = "NO MATCH";

		try {
			// FileReader reads text files in the default
			// encoding.
			FileReader fileReader = new FileReader(fileName);

			// Always wrap FileReader in BufferedReader.
			BufferedReader bufferedReader = new BufferedReader(fileReader);

			while ((line = bufferedReader.readLine()) != null) {
				System.out.println("> " + line);
				line = line.replace("\n", "");
				String pattern2 = "(/iplant/home/araport/rnaseq_bam/[a-zA-Z]*/([A-Z0-9a-z]*)/accepted_hits.bam)";

				Pattern r2 = Pattern.compile(pattern2, Pattern.MULTILINE);
				Matcher m2 = r2.matcher(line);

				if (m2.matches()) {
					// System.out.println(">>>> FOUND
					// IT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
					String new_exp = m2.group(2);

					System.out.println("'" + new_exp + "'" + " == " + "'" + ori_exp + "'");

					String new_url = m2.group(1);

					if (ori_exp.equals(new_exp)) {
						ret = "http://vision.iplantcollaborative.org"
								+ m2.group().replace("\n", "").replace("\r", "");
						System.out.println(
								">>>> !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
					}
				} else {
					System.out.println("NOT FOUND...");
				}
			}

			// Always close files.
			bufferedReader.close();
		} catch (FileNotFoundException ex) {
			System.out.println("Unable to open file '" + fileName + "'");
		} catch (IOException ex) {
			System.out.println("Error reading file '" + fileName + "'");
			// Or we could just do this:
			// ex.printStackTrace();
		}
		return ret;

	}
}