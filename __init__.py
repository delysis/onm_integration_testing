import os, platform, subprocess
from pathlib import Path

thisDir = os.path.abspath(os.path.dirname(__file__))

def check_instantiated():
	''' Check whether ONM was previously instantiated and working. '''
	return os.path.isfile(f'{thisDir}/instantiated.txt')

def runCommands(commandList : list):
	for x in commandList:
		print(f'Running {x}')
		os.system(x)

def install_onm(target : list = platform.system()):
	''' WARNING, WIP. TODO: Linux support, license check, tests. '''
	installCmd = {
		'Darwin' : [
			'sudo cat /Library/gurobi/gurobi.lic',
			'HOMEBREW_NO_AUTO_UPDATE=1 brew install julia',
			'wget "https://packages.gurobi.com/9.1/gurobi9.1.2_mac64.pkg"',
			'sudo installer -pkg gurobi9.1.2_mac64.pkg -target /',
			'echo "export GUROBI_HOME=/Library/gurobi912/mac64" >> ~/.zshrc',
			'echo "export PATH=/Library/gurobi912/mac64/bin:$PATH" >> ~/.zshrc',
			'echo "export LD_LIBRARY_PATH=/Library/gurobi912/mac64/lib" >> ~/.zshrc',
			'source ~/.zshrc',
			'''julia -e 'import Pkg; Pkg.add("Gurobi")' ''',
			'''julia -e 'import Pkg; Pkg.build("Gurobi")' ''',
			'''julia -e 'import Pkg; Pkg.add(Pkg.PackageSpec(;name="PowerModelsDistribution", version="2.1.0"));' ''',
			'''julia -e 'import Pkg; Pkg.add(Pkg.PackageSpec(;name="PowerModelsONM", version="2.1.0"));' ''',
			f'touch {thisDir}/instantiated.txt'
		],
		'Linux' : [
			'rm "julia-1.7.0-linux-x86_64.tar.gz"',
			'wget "https://julialang-s3.julialang.org/bin/linux/x64/1.7/julia-1.7.0-linux-x86_64.tar.gz"',
			'tar -x -f "julia-1.7.0-linux-x86_64.tar.gz" -C /usr/local --strip-components 1',
			'pip install julia',
			'rm "gurobi9.1.2_linux64.tar.gz"',
			'wget "https://packages.gurobi.com/9.1/gurobi9.1.2_linux64.tar.gz"',
			'tar -x -f "gurobi9.1.2_linux64.tar.gz"',
			'echo "export GUROBI_HOME=/content/gurobi912/linux64" >> ./bashrc',
			'echo "export PATH=/content/gurobi912/linux64/bin:$PATH" >> ./bashrc',
			'echo "export LD_LIBRARY_PATH=/content/gurobi912/linux64/lib:$PATH" >> ./bashrc',
			'source ~/.bashrc',
			'''julia -e 'import Pkg; Pkg.add("Gurobi")' ''',
			'''julia -e 'import Pkg; Pkg.build("Gurobi")' ''',
			'''julia -e 'import Pkg; Pkg.add(Pkg.PackageSpec(;name="PowerModelsDistribution", version="2.1.0"));’ ''',
			'''julia -e 'import Pkg; Pkg.add(Pkg.PackageSpec(;name="PowerModelsONM", version="2.1.0"));' ''',
			f'touch {thisDir}/instantiated.txt'
		]
	}
	runCommands(installCmd.get(target,'Linux'))

def build_settings_file(circuitPath='circuit.dss',settingsPath='settings.json', max_switch_actions=1, vm_lb_pu=0.9, vm_ub_pu=1.1, sbase_default=0.001, line_limit_mult='Inf', vad_deg=5.0):
	runCommands([f'''julia -e 'using PowerModelsONM; build_settings_file("{circuitPath}", "{settingsPath}"; max_switch_actions={max_switch_actions}, vm_lb_pu={vm_lb_pu}, vm_ub_pu={vm_ub_pu}, sbase_default={sbase_default}, line_limit_mult={line_limit_mult}, vad_deg={vad_deg})' '''])

def run_onm(circuitPath='circuit.dss', settingsPath='settings.json', outputPath="onm_out.json", eventsPath="events.json", gurobi='true', verbose='true', optSwitchSolver="mip_solver", fixSmallNumbers='true', skipList='["faults","stability"]'):
	runCommands([f'''julia -e 'import Gurobi; using PowerModelsONM; args = Dict{{String,Any}}("network"=>"{circuitPath}", "settings"=>"{settingsPath}", "output"=>"{outputPath}", "events"=>"{eventsPath}", "gurobi"=>{gurobi}, "verbose"=>{verbose}, "opt-switch-solver"=>"{optSwitchSolver}", "fix-small-numbers"=>{fixSmallNumbers}, "skip"=>{skipList}); entrypoint(args);' '''])

if __name__ == '__main__':
	# Basic Tests
	thisDirPath = Path(thisDir)
	omfDir = thisDirPath.parent.parent.absolute()
	install_onm()
	build_settings_file(circuitPath=f'./iowa240.network.reduced.dss', settingsPath='./settings.json', max_switch_actions=1, vm_lb_pu=0.9, vm_ub_pu=1.1, sbase_default=0.001, line_limit_mult='Inf', vad_deg=5.0)
	run_onm(circuitPath=f'./iowa240.network.reduced.dss', settingsPath='./settings.json', outputPath="./onm_out.json", eventsPath=f'./iowa240.events.json', gurobi='true', verbose='true', optSwitchSolver="mip_solver", fixSmallNumbers='true', skipList='["faults","stability"]')
