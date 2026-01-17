"""
Simple Project Manager for Battery Simulator.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from src.utils.file_operations import TemplateManager, FileOperationError

logger = logging.getLogger(__name__)


class ProjectManager:
    """Simple project manager for Battery Simulator projects."""
    
    # Map UI module names to actual template paths
    TEMPLATE_PATHS = {
        "SPM": "SPM/SPMFoam/Case",
        "halfCell": "halfCell/halfCellFoam/CC",
        "fullCell": "fullCell/fullCellFoam/case"
    }

    def __init__(self, base_projects_path: Union[str, Path]):
        self.base_projects_path = Path(base_projects_path)
        self.base_projects_path.mkdir(parents=True, exist_ok=True)
        
        templates_path = Path(__file__).parent.parent / "resources" / "templates"
        self.template_manager = TemplateManager(str(templates_path))
        
        logger.info(f"ProjectManager initialized with base path: {base_projects_path}")

    def create_project(
        self,
        project_name: str,
        template_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new project from a template."""
        try:
            project_path = self.base_projects_path / project_name
            
            if project_path.exists():
                logger.error(f"Project {project_name} already exists")
                return False
            
            # Map template name to actual path
            actual_template_path = self.TEMPLATE_PATHS.get(template_name, template_name)
            logger.info(f"Using template path: {actual_template_path}")
            
            # Copy template
            success = self.template_manager.copy_template_directory(
                actual_template_path,
                str(project_path)
            )
            
            if not success:
                logger.error(f"Failed to copy template {actual_template_path}")
                return False
            
            # Create metadata
            metadata = {
                'project_name': project_name,
                'template_name': template_name,
                'creation_date': datetime.now().isoformat(),
                'parameters': parameters or {}
            }
            
            metadata_path = project_path / 'project_metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Project {project_name} created at {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create project {project_name}: {e}", exc_info=True)
            return False

    def list_projects(self) -> List[str]:
        """List all projects."""
        try:
            if not self.base_projects_path.exists():
                return []
            
            projects = []
            for item in self.base_projects_path.iterdir():
                if item.is_dir() and (item / 'project_metadata.json').exists():
                    projects.append(item.name)
            
            return projects
            
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    def get_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project information."""
        try:
            metadata_path = self.base_projects_path / project_name / 'project_metadata.json'
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to get project info for {project_name}: {e}")
            return None

    def delete_project(self, project_name: str) -> bool:
        """Delete a project."""
        try:
            project_path = self.base_projects_path / project_name
            
            if not project_path.exists():
                logger.error(f"Project {project_name} does not exist")
                return False
            
            shutil.rmtree(project_path)
            logger.info(f"Project {project_name} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_name}: {e}")
            return False
