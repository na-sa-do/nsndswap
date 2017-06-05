import java.io.File;
import java.lang.String;

import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.exporter.spi.GraphExporter;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingold;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingoldBuilder;
import org.gephi.layout.plugin.labelAdjust.LabelAdjust;
import org.gephi.layout.plugin.labelAdjust.LabelAdjustBuilder;
import org.gephi.layout.plugin.noverlap.NoverlapLayout;
import org.gephi.layout.plugin.noverlap.NoverlapLayoutBuilder;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;

public class GephiBridge {
    private static final float AREA_FACTOR = 1.461560947f; // area per node

    public static void main(String[] args) throws Exception {
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        ImportController ic = Lookup.getDefault().lookup(ImportController.class);
        Container container = ic.importFile(new File(args[0]));
        container.verify();
        ic.process(container, new DefaultProcessor(), workspace);

        GraphController gc = Lookup.getDefault().lookup(GraphController.class);
        GraphModel gm = gc.getGraphModel();
        FruchtermanReingold fr = new FruchtermanReingoldBuilder().buildLayout();
        fr.setGraphModel(gm);
        fr.initAlgo();
        fr.resetPropertiesValues();
        fr.setArea(GephiBridge.AREA_FACTOR * gc.getGraphModel().getGraph().getNodeCount());
        fr.setSpeed(2d);
        for (int i = 0; i < 2000 && fr.canAlgo(); i++) {
            System.out.println("Running FR iteration number " + String.valueOf(i) + " on " + args[0]);
            fr.goAlgo();
        }
        fr.endAlgo();
        NoverlapLayout no = (NoverlapLayout) new NoverlapLayoutBuilder().buildLayout();
        no.setGraphModel(gm);
        no.initAlgo();
        no.resetPropertiesValues();
        for (int i = 0; i < 50 && no.canAlgo(); i++) {
            System.out.println("Running NO iteration number " + String.valueOf(i) + " on " + args[0]);
            no.goAlgo();
        }
        no.endAlgo();
        LabelAdjust la = new LabelAdjustBuilder().buildLayout();
        la.setGraphModel(gm);
        la.initAlgo();
        la.resetPropertiesValues();
        for (int i = 0; i < 50 && la.canAlgo(); i++) {
            System.out.println("Running LA iteration number " + String.valueOf(i) + " on " + args[0]);
            la.goAlgo();
        }
        la.endAlgo();

        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        GraphExporter gexfExporter = (GraphExporter) ec.getExporter("gexf");
        gexfExporter.setWorkspace(workspace);
        ec.exportFile(new File(args[0]), gexfExporter);
    }
}
