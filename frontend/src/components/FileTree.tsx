import React, { useState } from 'react';
import { Folder, FolderOpen, FileCode, FileText, File, ChevronRight, ChevronDown } from 'lucide-react';
import { Artifact } from '../types';

interface FileTreeProps {
  artifacts: Artifact[];
  selectedFile: string | null;
  onSelectFile: (artifact: Artifact) => void;
}

interface TreeNode {
  name: string;
  path: string;
  isFolder: boolean;
  children: { [key: string]: TreeNode };
  artifact?: Artifact;
}

function buildTree(artifacts: Artifact[]): TreeNode {
  const root: TreeNode = { name: '', path: '', isFolder: true, children: {} };

  artifacts.forEach((artifact) => {
    const parts = artifact.relative_path.split('/');
    let current = root;

    parts.forEach((part, index) => {
      const isLast = index === parts.length - 1;
      const currentPath = parts.slice(0, index + 1).join('/');

      if (!current.children[part]) {
        current.children[part] = {
          name: part,
          path: currentPath,
          isFolder: !isLast,
          children: {},
          artifact: isLast ? artifact : undefined,
        };
      }
      current = current.children[part];
    });
  });

  return root;
}

const FileIcon: React.FC<{ name: string }> = ({ name }) => {
  if (name.endsWith('.py') || name.endsWith('.ts') || name.endsWith('.tsx') || name.endsWith('.js')) {
    return <FileCode className="w-4 h-4 text-sky-400" />;
  }
  if (name.endsWith('.md') || name.endsWith('.txt')) {
    return <FileText className="w-4 h-4 text-emerald-400" />;
  }
  return <File className="w-4 h-4 text-slate-400" />;
};

const TreeItem: React.FC<{
  node: TreeNode;
  selectedFile: string | null;
  onSelectFile: (artifact: Artifact) => void;
  level: number;
}> = ({ node, selectedFile, onSelectFile, level }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (node.isFolder) {
    const childrenKeys = Object.keys(node.children).sort((a, b) => {
      // Folders first, then files
      const aFolder = node.children[a].isFolder;
      const bFolder = node.children[b].isFolder;
      if (aFolder && !bFolder) return -1;
      if (!aFolder && bFolder) return 1;
      return a.localeCompare(b);
    });

    return (
      <div>
        <div
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-1.5 py-1 px-2 rounded-md hover:bg-slate-800/60 cursor-pointer text-slate-300 select-none text-xs"
          style={{ paddingLeft: `${level * 12 + 8}px` }}
        >
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
          )}
          {isOpen ? (
            <FolderOpen className="w-4 h-4 text-amber-400" />
          ) : (
            <Folder className="w-4 h-4 text-amber-400" />
          )}
          <span className="font-medium text-slate-200">{node.name}</span>
        </div>

        {isOpen && (
          <div>
            {childrenKeys.map((key) => (
              <TreeItem
                key={node.children[key].path}
                node={node.children[key]}
                selectedFile={selectedFile}
                onSelectFile={onSelectFile}
                level={level + 1}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  const isSelected = selectedFile === node.artifact?.id;

  return (
    <div
      onClick={() => node.artifact && onSelectFile(node.artifact)}
      className={`flex items-center gap-2 py-1 px-2 rounded-md cursor-pointer text-xs select-none transition-colors ${
        isSelected
          ? 'bg-indigo-600/20 text-indigo-300 font-medium border border-indigo-500/30'
          : 'hover:bg-slate-800/60 text-slate-300'
      }`}
      style={{ paddingLeft: `${level * 12 + 20}px` }}
    >
      <FileIcon name={node.name} />
      <span className="truncate">{node.name}</span>
    </div>
  );
};

export const FileTree: React.FC<FileTreeProps> = ({ artifacts, selectedFile, onSelectFile }) => {
  const tree = buildTree(artifacts);
  const rootKeys = Object.keys(tree.children).sort();

  if (artifacts.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-slate-500">
        No generated artifacts yet.
      </div>
    );
  }

  return (
    <div className="py-2 overflow-y-auto max-h-[600px]">
      {rootKeys.map((key) => (
        <TreeItem
          key={tree.children[key].path}
          node={tree.children[key]}
          selectedFile={selectedFile}
          onSelectFile={onSelectFile}
          level={0}
        />
      ))}
    </div>
  );
};
