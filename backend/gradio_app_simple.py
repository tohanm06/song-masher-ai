"""
Simple Gradio App for PoC Mode (No Essentia Required)
Single-file demo of Song Masher AI functionality.
"""

import os
import tempfile
import gradio as gr
import numpy as np
import soundfile as sf
from analysis_simple import AudioAnalyzer
from separation import StemSeparator
from planning import MashupPlanner
from render import MashupRenderer

# Initialize components
analyzer = AudioAnalyzer()
separator = StemSeparator()
planner = MashupPlanner()
renderer = MashupRenderer()

def analyze_audio(audio_file):
    """Analyze uploaded audio file."""
    if audio_file is None:
        return "Please upload an audio file", None
    
    try:
        # Analyze audio
        result = analyzer.analyze(audio_file)
        
        # Create summary
        summary = f"""
        **Analysis Results:**
        - Duration: {result['duration']:.1f}s
        - BPM: {result['bpm']:.1f}
        - Key: {result['key']} ({result['camelot']})
        - LUFS: {result['lufs']:.1f} dB
        - Beats: {len(result['beats'])}
        - Sections: {len(result['sections'])}
        """
        
        return summary, result
    except Exception as e:
        return f"Analysis failed: {str(e)}", None

def separate_stems(audio_file):
    """Separate audio into stems."""
    if audio_file is None:
        return "Please upload an audio file", None, None, None, None
    
    try:
        # Separate stems
        stems = separator.separate(audio_file)
        
        # Return stem paths
        return (
            stems.get('vocals', ''),
            stems.get('drums', ''),
            stems.get('bass', ''),
            stems.get('other', '')
        )
    except Exception as e:
        return f"Separation failed: {str(e)}", None, None, None, None

def create_mashup_plan(track_a_analysis, track_b_analysis, recipe):
    """Create mashup plan from two track analyses."""
    if not track_a_analysis or not track_b_analysis:
        return "Please analyze both tracks first", None
    
    try:
        # Create plan
        plan = planner.create_plan(track_a_analysis, track_b_analysis, recipe)
        
        # Create summary
        summary = f"""
        **Mashup Plan:**
        - Recipe: {recipe}
        - Target Key: {plan['targetKey']}
        - Key Shifts: A={plan['keyShiftA']}, B={plan['keyShiftB']}
        - Target BPM: {plan['stretchMap']['targetBpm']:.1f}
        - Stretch Ratios: A={plan['stretchMap']['stretchA']:.2f}x, B={plan['stretchMap']['stretchB']:.2f}x
        - Section Pairs: {len(plan['sectionPairs'])}
        - Quality Hints: {len(plan['qualityHints'])}
        """
        
        return summary, plan
    except Exception as e:
        return f"Planning failed: {str(e)}", None

def render_mashup(stems, plan, mix_params):
    """Render final mashup."""
    if not stems or not plan:
        return "Please complete separation and planning first", None
    
    try:
        # Render mashup
        output_path = renderer.render(stems, plan, mix_params)
        
        return "Mashup rendered successfully!", output_path
    except Exception as e:
        return f"Rendering failed: {str(e)}", None

def create_demo_interface():
    """Create Gradio interface."""
    with gr.Blocks(title="Song Masher AI - PoC Mode") as demo:
        gr.Markdown("# 🎵 Song Masher AI - PoC Mode")
        gr.Markdown("Upload two audio files to create a professional mashup!")
        
        with gr.Tabs():
            # Analysis Tab
            with gr.Tab("Analysis"):
                gr.Markdown("## Audio Analysis")
                
                with gr.Row():
                    with gr.Column():
                        audio_input = gr.Audio(label="Upload Audio File", type="filepath")
                        analyze_btn = gr.Button("Analyze Audio", variant="primary")
                        analysis_output = gr.Markdown()
                        analysis_data = gr.State()
                
                analyze_btn.click(
                    analyze_audio,
                    inputs=[audio_input],
                    outputs=[analysis_output, analysis_data]
                )
            
            # Separation Tab
            with gr.Tab("Stem Separation"):
                gr.Markdown("## Stem Separation")
                
                with gr.Row():
                    with gr.Column():
                        separation_input = gr.Audio(label="Upload Audio File", type="filepath")
                        separate_btn = gr.Button("Separate Stems", variant="primary")
                        separation_output = gr.Markdown()
                
                with gr.Row():
                    vocals_output = gr.Audio(label="Vocals", type="filepath")
                    drums_output = gr.Audio(label="Drums", type="filepath")
                    bass_output = gr.Audio(label="Bass", type="filepath")
                    other_output = gr.Audio(label="Other", type="filepath")
                
                separate_btn.click(
                    separate_stems,
                    inputs=[separation_input],
                    outputs=[separation_output, vocals_output, drums_output, bass_output, other_output]
                )
            
            # Planning Tab
            with gr.Tab("Mashup Planning"):
                gr.Markdown("## Mashup Planning")
                
                with gr.Row():
                    with gr.Column():
                        track_a_data = gr.State()
                        track_b_data = gr.State()
                        recipe_select = gr.Dropdown(
                            choices=["AoverB", "BoverA", "HybridDrums"],
                            value="AoverB",
                            label="Mashup Recipe"
                        )
                        plan_btn = gr.Button("Create Plan", variant="primary")
                        plan_output = gr.Markdown()
                        plan_data = gr.State()
                
                plan_btn.click(
                    create_mashup_plan,
                    inputs=[track_a_data, track_b_data, recipe_select],
                    outputs=[plan_output, plan_data]
                )
            
            # Rendering Tab
            with gr.Tab("Rendering"):
                gr.Markdown("## Final Rendering")
                
                with gr.Row():
                    with gr.Column():
                        stems_data = gr.State()
                        plan_data_render = gr.State()
                        mix_params = gr.JSON(
                            value={
                                "vocals_gain": 1.0,
                                "drums_gain": 0.8,
                                "bass_gain": 0.7,
                                "other_gain": 0.6,
                                "auto_eq": True,
                                "sidechain_ducking": True,
                                "de_esser": True
                            },
                            label="Mix Parameters"
                        )
                        render_btn = gr.Button("Render Mashup", variant="primary")
                        render_output = gr.Markdown()
                        final_output = gr.Audio(label="Final Mashup", type="filepath")
                
                render_btn.click(
                    render_mashup,
                    inputs=[stems_data, plan_data_render, mix_params],
                    outputs=[render_output, final_output]
                )
        
        # Demo instructions
        gr.Markdown("""
        ## Demo Instructions
        
        1. **Analysis**: Upload an audio file and click "Analyze Audio"
        2. **Separation**: Upload an audio file and click "Separate Stems" 
        3. **Planning**: Use the analysis results to create a mashup plan
        4. **Rendering**: Render the final mashup with your chosen parameters
        
        **Note**: This is a simplified PoC version. For production use, deploy the full Docker stack.
        """)
    
    return demo

if __name__ == "__main__":
    # Check if running in simple mode
    if os.getenv("SIMPLE_MODE", "false").lower() == "true":
        demo = create_demo_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    else:
        print("SIMPLE_MODE not enabled. Use SIMPLE_MODE=true to run Gradio app.")
