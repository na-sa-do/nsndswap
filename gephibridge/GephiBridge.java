import java.io.File;

import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
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
    }
}
