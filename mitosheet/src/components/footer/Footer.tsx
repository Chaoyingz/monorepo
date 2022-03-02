// Copyright (c) Mito

import React from 'react';
import SheetTab from './SheetTab';

// import css
import "../../../css/footer.css"
import MitoAPI from '../../api';
import { TaskpaneType } from '../taskpanes/taskpanes';
import PlusIcon from '../icons/PlusIcon';
import { GraphDataJSON, GridState, SheetData, UIState } from '../../types';

type FooterProps = {
    sheetDataArray: SheetData[];
    graphDataJSON: GraphDataJSON;
    gridState: GridState;
    setGridState: React.Dispatch<React.SetStateAction<GridState>>;
    mitoAPI: MitoAPI;
    closeOpenEditingPopups: () => void;
    uiState: UIState;
    setUIState: React.Dispatch<React.SetStateAction<UIState>>;
    mitoContainerRef: React.RefObject<HTMLDivElement>;
};

/*
    Wrapper component that displays the entire footer of the sheet, including
    the sheet tabs, as well as the shape of the currently selected dataframe.
*/
function Footer(props: FooterProps): JSX.Element {

    const selectedSheetIndex = props.uiState.selectedSheetIndex
    const selectedGraphID = props.uiState.selectedGraphID
    const sheetData: SheetData | undefined = props.sheetDataArray[selectedSheetIndex];
    const selectedTabType = props.uiState.selectedTabType

    return (
        <div className='footer'>
            <div
                className='footer-add-button'
                onClick={() => {
                    props.setUIState(prevUIState => {
                        return {
                            ...prevUIState,
                            currOpenTaskpane: {type: TaskpaneType.IMPORT}
                        }
                    })
                }}
            >
                <PlusIcon/>
            </div>
            <div className="footer-tab-bar">
                {/* First add the data tabs, and then add the graph tabs */}
                {props.sheetDataArray.map(df => df.dfName).map((dfName, idx) => {
                    return (
                        <SheetTab
                            key={idx}
                            tabName={dfName}
                            tabIDObj={{tabType: 'data', selectedIndex: idx}}
                            isSelectedTab={selectedTabType === 'data' && idx === selectedSheetIndex}
                            setUIState={props.setUIState}
                            closeOpenEditingPopups={props.closeOpenEditingPopups}
                            mitoAPI={props.mitoAPI}
                            mitoContainerRef={props.mitoContainerRef}
                        />
                    )
                })}
                {Object.entries(props.graphDataJSON).map(([graphID, graphData]) => {
                    console.log(graphData.graphParams)
                    return (
                        <SheetTab
                            key={graphID}
                            tabName={graphID}
                            tabIDObj={{tabType: 'graph', graphID: graphID}}
                            isSelectedTab={selectedTabType === 'graph' && graphID === selectedGraphID}
                            setUIState={props.setUIState}
                            closeOpenEditingPopups={props.closeOpenEditingPopups}
                            mitoAPI={props.mitoAPI}
                            mitoContainerRef={props.mitoContainerRef}
                        />
                    )
                })}
            </div>

            {/*TODO: Figure out what to display here when the graph tab is displayed!*/}
            {sheetData !== undefined && 
                <div className='footer-right-side'>
                    <div className='footer-sheet-shape'>
                        ({sheetData.numRows} rows, {sheetData.numColumns} cols)
                    </div>
                </div>
            }
        </div>
    );
}

export default Footer;
