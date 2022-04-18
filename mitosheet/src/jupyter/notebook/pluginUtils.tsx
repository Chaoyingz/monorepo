import MitoAPI from "../api";
import { getCodeString } from "../../utils/code";

type CellType = any;

export function getCellAtIndex(index: number): CellType | undefined {
    return (window as any).Jupyter?.notebook?.get_cell(index);
}

export function getCellText(cell: CellType | undefined): string {
    return cell?.get_text() || '';
}

// TODO: deduplicate this in shared utils
export function getLastNonEmptyLine(cell: CellType | undefined): string | undefined {
    if (cell === undefined) {
        return undefined
    }
    const activeCellText = getCellText(cell)
    const filteredActiveText = activeCellText.split(/\r?\n/).filter(line => line.trim().length > 0)
    return filteredActiveText.length > 0 ? filteredActiveText.pop() : undefined
}

export const getArgsFromMitosheetCallCell = (mitosheetCallCell: CellType | undefined): string[] => {
    const content = getCellText(mitosheetCallCell);

    let nameString = content.split('mitosheet.sheet(')[1].split(')')[0];

    // If there is a (new) analysis name parameter passed, we ignore it
    if (nameString.includes('analysis_to_replay')) {
        nameString = nameString.split('analysis_to_replay')[0].trim();
    }

    // If there is a view_df name parameter, we ignore it
    // TODO: remove this on Jan 1, 2023 (since we no longer need it)
    if (nameString.includes('view_df')) {
        nameString = nameString.split('view_df')[0].trim();
    }

    // Get the args and trim them up
    let args = nameString.split(',').map(dfName => dfName.trim());
    
    // Remove any names that are empty. Note that some of these names
    // may be strings, which we turn into valid df_names on the backend!
    args = args.filter(dfName => {return dfName.length > 0});

    return args;
}


// Returns true iff a the given cell ends with a mitosheet.sheet call
export function isMitosheetCallCell(cell: CellType | undefined): boolean {
    const currentCode = getCellText(cell);

    // Take all the non-empty lines from the cell
    const lines = currentCode.split('\n').filter(line => {return line.length > 0});
    if (lines.length == 0) {
        return false;
    }

    const lastLine = lines[lines.length - 1];
    /* 
        We check if the last line contains a mitosheet.sheet call, which can happen in a few ways
        
        1. `import mitosheet` -> mitosheet.sheet()
        2. `import mitosheet as {THING}` -> {THING}.sheet(
        3. `from mitosheet import sheet` -> sheet(

        We detect all three by checking if the line contains `sheet(`!
    */

    return lastLine.indexOf('sheet(') !== -1;
}



// Returns true iff a the given cell is a cell containing the generated code
function isMitoAnalysisCell(cell: CellType | undefined): boolean {
    const currentCode = getCellText(cell);
    // Handle the old and new Mito boilerplate code
    return currentCode.startsWith('# MITO CODE START') 
        || currentCode.startsWith('from mitosheet import *; register_analysis(')
        || currentCode.startsWith('from mitosheet import *; # Analysis:')
        || currentCode.startsWith('from mitosheet import *; # Analysis Name:')
}


/* 
    Returns true if the cell contains a mitosheet.sheet(analysis_to_replay={analysisName})
*/
export function containsMitosheetCallWithSpecificAnalysisToReplay(cell: CellType | undefined, analysisName: string): boolean {
    const currentCode = getCellText(cell);
    return currentCode.includes('sheet(') && currentCode.includes(`analysis_to_replay="${analysisName}"`)
}

/* 
    Returns true if the cell contains a mitosheet.sheet(analysis_to_replay={analysisName})
*/
export function containsMitosheetCallWithAnyAnalysisToReplay(cell: CellType | undefined): boolean {
    const currentCode = getCellText(cell);
    return isMitosheetCallCell(cell) && currentCode.includes(`analysis_to_replay=`)
}

/* 
    Returns true if the cell contains the code generated for a specific analysis name
*/
export function containsGeneratedCodeOfAnalysis(cell: CellType | undefined, analysisName: string): boolean {
    const currentCode = getCellText(cell);
    return isMitoAnalysisCell(cell) && currentCode.includes(analysisName);
}

/* 
    Returns True if the passed cell is empty.
    Returns False if the passed cells is either not empty or undefined 
*/
export function isEmptyCell(cell: CellType | undefined): boolean {
    if (cell === undefined) {
        return false;
    }
    const currentCode = getCellText(cell);
    return currentCode.trim() === '';
}

/**
 * Returns the cell that has the mitosheet.sheet(analysis_to_replay={analysisName}) in it,
 * or undefined if no such cell exists
 */
export function getCellCallingMitoshetWithAnalysis(analysisName: string): [CellType, number] | undefined  {
    const cells: CellType[] = (window as any).Jupyter?.notebook?.get_cells();

    if (cells === undefined) {
        return undefined;
    }

    let cellIndex = 0;
    for (const cell of cells) {
        if (containsMitosheetCallWithSpecificAnalysisToReplay(cell, analysisName)) {
            return [cell, cellIndex];
        }

        cellIndex++;
    }

    return undefined;
}


/**
 * A function that returns the [cell, index] pair of the mitosheet.sheet() call that contains
 * the analysis name. 
 * 
 * If no mitosheet.sheet() call contains this analysis name, then we assume it hasen't been 
 * written yet, and take our best guess at which sheet this is.
 * 
 * Returns undefined if it can find no good guess for a calling mitosheet cell.
 */
export function getMostLikelyMitosheetCallingCell(analysisName: string | undefined): [CellType, number] | undefined {

    // First, we check if this analysis name is in a mitosheet call, in which case things are easy
    if (analysisName) {
        const mitosheetCallCellAndIndex = getCellCallingMitoshetWithAnalysis(analysisName);
        if (mitosheetCallCellAndIndex !== undefined) {
            return mitosheetCallCellAndIndex;
        }
    }

    const cells = (window as any).Jupyter?.notebook?.get_cells();

    if (cells == undefined) {
        return;
    }

    const activeCell = (window as any).Jupyter?.notebook?.get_cell((window as any).Jupyter?.notebook?.get_anchor_index());
    const activeCellIndex = (window as any).Jupyter?.notebook?.get_anchor_index() || 0;

    const previousCell = getCellAtIndex(activeCellIndex - 1)

    // As the most common way for a user to run a cell for the first time is to run and advanced, this 
    // means that the active cell will most likely be one below the mitosheet.sheet() call we want to 
    // write to, so we check this first
    if (previousCell && isMitosheetCallCell(previousCell) && !containsMitosheetCallWithAnyAnalysisToReplay(previousCell)) {
        return [previousCell, activeCellIndex - 1];
    } 

    // The next case we check is if they did a run and not advance, which means that the currently
    // selected cell is the mitosheet.sheet call
    if (activeCell && isMitosheetCallCell(activeCell) && !containsMitosheetCallWithAnyAnalysisToReplay(activeCell)) {
        return [activeCell, activeCellIndex];
    }

    // The last case is that the user did some sort of run all, in which case we cross our fingers
    // that there is only one cell that does not have a mitosheet call with an analysis_to_replay, 
    // and go looking for it
    let index = activeCellIndex;
    while (index >= 0) {
        const cell = getCellAtIndex(index)
        if (cell && isMitosheetCallCell(cell) && !containsMitosheetCallWithAnyAnalysisToReplay(cell)) {
            return [cell, index];
        }
        index--;
    }

    return undefined;
}

export function writeToCell(cell: CellType | undefined, code: string): void {
    if (cell == undefined) {
        return;
    }
    cell.set_text(code);
}


/**
 * Given a cell, will check if it has a mitosheet.sheet() call with the old
 * analysis to replay, and if so will replace it with the new analysis to 
 * replay
 */
export function tryOverwriteAnalysisToReplayParameter(cell: CellType | undefined, oldAnalysisName: string, newAnalysisName: string): boolean {
    if (isMitosheetCallCell(cell) && containsMitosheetCallWithSpecificAnalysisToReplay(cell, oldAnalysisName)) {
        const currentCode = getCellText(cell);

        const newCode = currentCode.replace(
            `analysis_to_replay="${oldAnalysisName}")`,
            `analysis_to_replay="${newAnalysisName}")`
        )
        writeToCell(cell, newCode);
        return true;
    } 

    return false;
}

/**
 * Given a cell, will check if it has a mitosheet.sheet() call with no
 * analysis_to_replay, and if so add the analysisName as a parameter to
 * this cell. It will return true in this case. 
 * 
 * Otherwise, if this is not a mitosheet.sheet() call, or if it already has
 * a analysis_to_replay parameter, this will return false.
 */
export function tryWriteAnalysisToReplayParameter(cell: CellType | undefined, analysisName: string): boolean {
    if (isMitosheetCallCell(cell) && !containsMitosheetCallWithAnyAnalysisToReplay(cell)) {
        const currentCode = getCellText(cell);

        // We know the mitosheet.sheet() call is the last thing in the cell, so we 
        // just replace the last closing paren
        const lastIndex = currentCode.lastIndexOf(')');
        let replacement = ``;
        if (currentCode.includes('sheet()')) {
            replacement = `analysis_to_replay="${analysisName}")`;
        } else {
            replacement = `, analysis_to_replay="${analysisName}")`;
        }
        const newCode = currentCode.substring(0, lastIndex) + replacement + currentCode.substring(lastIndex + 1);
        writeToCell(cell, newCode);
        return true;
    } 

    return false;
}


export const notebookGetArgs = (analysisToReplayName: string | undefined): string[] => {
    const cellAndIndex = getMostLikelyMitosheetCallingCell(analysisToReplayName);
    if (cellAndIndex) {
        const [cell, ] = cellAndIndex;
        return getArgsFromMitosheetCallCell(cell);
    } else {
        return [];
    }
}

export const notebookWriteAnalysisToReplayToMitosheetCall = (analysisName: string, mitoAPI: MitoAPI): void => {
    const cellAndIndex = getMostLikelyMitosheetCallingCell(analysisName);

    if (cellAndIndex) {
        const [cell, ] = cellAndIndex;
        const written = tryWriteAnalysisToReplayParameter(cell, analysisName);
        if (written) {
            return;
        }
    } 

    // Log if we are unable to write this param for any reason
    void mitoAPI.log('write_analysis_to_replay_to_mitosheet_call_failed');
}

export const notebookOverwriteAnalysisToReplayToMitosheetCall = (oldAnalysisName: string, newAnalysisName: string, mitoAPI: MitoAPI): void => {

    const mitosheetCallCellAndIndex = getCellCallingMitoshetWithAnalysis(oldAnalysisName);
    if (mitosheetCallCellAndIndex === undefined) {
        return;
    }

    const [mitosheetCallCell, ] = mitosheetCallCellAndIndex;

    const overwritten = tryOverwriteAnalysisToReplayParameter(mitosheetCallCell, oldAnalysisName, newAnalysisName);
    if (!overwritten) {
        void mitoAPI.log('overwrite_analysis_to_replay_to_mitosheet_call_failed');
    }
}

export const notebookWriteGeneratedCodeToCell = (analysisName: string, codeLines: string[], telemetryEnabled: boolean): void => {
    const code = getCodeString(analysisName, codeLines, telemetryEnabled);
        
    // Find the cell that made the mitosheet.sheet call, and if it does not exist, give
    // up immediately
    const mitosheetCallCellAndIndex = getCellCallingMitoshetWithAnalysis(analysisName);
    if (mitosheetCallCellAndIndex === undefined) {
        return;
    }

    const [, mitosheetCallIndex] = mitosheetCallCellAndIndex;

    const cells = (window as any).Jupyter?.notebook?.get_cells();

    if (cells === undefined) {
        return;
    }

    const activeCellIndex = (window as any).Jupyter?.notebook?.get_anchor_index() || 0;

    const codeCell = getCellAtIndex(mitosheetCallIndex + 1);

    if (isEmptyCell(codeCell) || containsGeneratedCodeOfAnalysis(codeCell, analysisName)) {
        writeToCell(codeCell, code)
    } else {
        // If we cannot write to the cell below, we have to go back a new cell below, 
        // which can eb a bit of an involve process
        if (mitosheetCallIndex !== activeCellIndex) {
            // We have to move our selection back up to the cell that we 
            // make the mitosheet call to 
            if (mitosheetCallIndex < activeCellIndex) {
                for (let i = 0; i < (activeCellIndex - mitosheetCallIndex); i++) {
                    (window as any).Jupyter?.notebook?.select_prev();
                }
            } else if (mitosheetCallIndex > activeCellIndex) {
                for (let i = 0; i < (mitosheetCallIndex - activeCellIndex); i++) {
                    (window as any).Jupyter?.notebook?.select_next();
                }
            }
        }
        // And then write to this new cell below, which is not the active cell but we
        // should make it the actice cell
        (window as any).Jupyter?.notebook?.insert_cell_below();
        (window as any).Jupyter?.notebook?.select_next();
        const activeCell = (window as any).Jupyter?.notebook?.get_cell((window as any).Jupyter?.notebook?.get_anchor_index());
        writeToCell(activeCell, code);
    }
}

