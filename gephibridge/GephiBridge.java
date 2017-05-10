import java.io.File;
import java.lang.String;

import org.gephi.graph.api.GraphController;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingold;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingoldBuilder;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;

public class GephiBridge {
    public static void main(String[] args) throws Exception {
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        ImportController ic = Lookup.getDefault().lookup(ImportController.class);
        Container container = ic.importFile(new File(args[0]));
        container.verify();
        ic.process(container, new DefaultProcessor(), workspace);

        GraphController gc = Lookup.getDefault().lookup(GraphController.class);
        FruchtermanReingold fr = new FruchtermanReingoldBuilder().buildLayout();
        fr.setGraphModel(gc.getGraphModel());
        fr.initAlgo();
        fr.resetPropertiesValues();
        fr.setSpeed(3d);
        for (int i = 0; i < 2000 && fr.canAlgo(); i++) {
            System.out.println("Running FR iteration number " + String.valueOf(i));
            fr.goAlgo();
        }
        fr.endAlgo();
    }
}
