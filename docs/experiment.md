# Experiment

This section describes different types of experimental data which
EasyDiffraction can handle.

## CIF-based description

The following examples show the CIF data blocks for different types of
diffraction experiments supported in EasyDiffraction.

### [pd-neut-cwl][3]{:.label-experiment}

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
data_<span class="red"><b>hrpt</b></span>

<span class="blue"><b>_diffrn_radiation</b>.probe</span>                 neutron
<span class="blue"><b>_diffrn_radiation_wavelength</b>.wavelength</span> 1.494

<span class="blue"><b>_pd_calib</b>.2theta_offset</span> 0.6225(4)

<span class="blue"><b>_pd_instr</b>.resolution_u</span>  0.0834
<span class="blue"><b>_pd_instr</b>.resolution_v</span> -0.1168
<span class="blue"><b>_pd_instr</b>.resolution_w</span>  0.123
<span class="blue"><b>_pd_instr</b>.resolution_x</span>  0
<span class="blue"><b>_pd_instr</b>.resolution_y</span>  0.0797

<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p1</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p2</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p3</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p4</span> 0

loop_
<span class="green"><b>_pd_phase_block</b>.id</span>
<span class="green"><b>_pd_phase_block</b>.scale</span>
lbco 9.0976(3)

loop_
<span class="green"><b>_pd_background</b>.line_segment_X</span>
<span class="green"><b>_pd_background</b>.line_segment_intensity</span>
<span class="green"><b>_pd_background</b>.X_coordinate</span>
 10  174.3  2theta
 20  159.8  2theta
 30  167.9  2theta
 50  166.1  2theta
 70  172.3  2theta
 90  171.1  2theta
110  172.4  2theta
130  182.5  2theta
150  173.0  2theta
165  171.1  2theta

loop_
<span class="green"><b>_pd_meas</b>.2theta_scan</span>
<span class="green"><b>_pd_meas</b>.intensity_total</span>
<span class="green"><b>_pd_meas</b>.intensity_total_su</span>
 10.00  167  12.6
 10.05  157  12.5
 10.10  187  13.3
 10.15  197  14.0
 10.20  164  12.5
 10.25  171  13.0
...
164.60  153  20.7
164.65  173  30.1
164.70  187  27.9
164.75  175  38.2
164.80  168  30.9
164.85  109  41.2
</pre>
</div>
<!-- prettier-ignore-end -->

### [pd-neut-tof][3]{:.label-experiment}

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
data_<span class="red"><b>wish</b></span>

<span class="blue"><b>_diffrn_radiation</b>.probe</span> neutron

<span class="blue"><b>_pd_instr</b>.2theta_bank</span> 152.827

<span class="blue"><b>_pd_instr</b>.dtt1</span> 20773.1(3)
<span class="blue"><b>_pd_instr</b>.dtt2</span>    -1.08308
<span class="blue"><b>_pd_instr</b>.zero</span>   -13.7(5)

<span class="blue"><b>_pd_instr</b>.alpha0</span> -0.009(1)
<span class="blue"><b>_pd_instr</b>.alpha1</span>  0.109(2)
<span class="blue"><b>_pd_instr</b>.beta0</span>   0.00670(3)
<span class="blue"><b>_pd_instr</b>.beta1</span>   0.0100(3)
<span class="blue"><b>_pd_instr</b>.sigma0</span>  0
<span class="blue"><b>_pd_instr</b>.sigma1</span>  0
<span class="blue"><b>_pd_instr</b>.sigma2</span> 15.7(8)

loop_
<span class="green"><b>_pd_phase_block</b>.id</span>
<span class="green"><b>_pd_phase_block</b>.scale</span>
ncaf 1.093(5)

loop_
<span class="green"><b>_pd_background</b>.line_segment_X</span>
<span class="green"><b>_pd_background</b>.line_segment_intensity</span>
<span class="green"><b>_pd_background</b>.X_coordinate</span>
  9162.3  465(38) time-of-flight
 11136.8  593(30) time-of-flight
 14906.5  546(18) time-of-flight
 17352.2  496(14) time-of-flight
 20179.5  452(10) time-of-flight
 22176.0  468(12) time-of-flight
 24644.7  380(6)  time-of-flight
 28257.2  378(4)  time-of-flight
 34034.4  328(4)  time-of-flight
 41214.6  323(3)  time-of-flight
 49830.9  273(3)  time-of-flight
 58204.9  260(4)  time-of-flight
 70186.9  262(5)  time-of-flight
 82103.2  268(5)  time-of-flight
102712.0  262(15) time-of-flight

loop_
<span class="green"><b>_pd_meas</b>.time_of_flight</span>
<span class="green"><b>_pd_meas</b>.intensity_total</span>
<span class="green"><b>_pd_meas</b>.intensity_total_su</span>
  9001.0  616.523  124.564
  9006.8  578.769  123.141
  9012.6  574.184  120.507
  9018.5  507.739  111.300
  9024.3  404.672  101.616
  9030.1  469.244  107.991
...
103085.0  275.072   60.978
103151.4  214.187   55.675
103217.9  256.211   62.825
103284.4  323.872   73.082
103351.0  242.382   65.736
103417.6  277.666   73.837
</pre>
</div>
<!-- prettier-ignore-end -->

### [sc-neut-cwl][3]{:.label-experiment}

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
data_<span class="red"><b>heidi</b></span>

<span class="blue"><b>_diffrn_radiation</b>.probe</span>                 neutron
<span class="blue"><b>_diffrn_radiation_wavelength</b>.wavelength</span> 0.793

<span class="blue"><b>_pd_calib</b>.2theta_offset</span> 0.6225(4)

<span class="blue"><b>_pd_instr</b>.resolution_u</span>  0.0834
<span class="blue"><b>_pd_instr</b>.resolution_v</span> -0.1168
<span class="blue"><b>_pd_instr</b>.resolution_w</span>  0.123
<span class="blue"><b>_pd_instr</b>.resolution_x</span>  0
<span class="blue"><b>_pd_instr</b>.resolution_y</span>  0.0797

<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p1</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p2</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p3</span> 0
<span class="blue"><b>_pd_instr</b>.reflex_asymmetry_p4</span> 0

loop_
<span class="green"><b>_exptl_crystal</b>.id</span>
<span class="green"><b>_exptl_crystal</b>.scale</span>
tbti 2.92(6)

loop_
<span class="green"><b>_refln</b>.index_h</span>
<span class="green"><b>_refln</b>.index_k</span>
<span class="green"><b>_refln</b>.index_l</span>
<span class="green"><b>_refln</b>.intensity_meas</span>
<span class="green"><b>_refln</b>.intensity_meas_su</span>
 1  1  1   194.5677    2.3253
 2  2  0    22.6319    1.1233
 3  1  1    99.2917    2.5620
 2  2  2   219.2877    3.2522
...
16  8  8    29.3063   12.6552
17  7  7  1601.5154  628.8915
13 13  7  1176.0896  414.6018
19  5  1     0.8334   20.4207
15  9  9    10.9864    8.0650
12 12 10    14.4074   11.3800
</pre>
</div>
<!-- prettier-ignore-end -->

## Other supported data files

If you do not have a CIF file with both the instrumental parameters and measured data, as in the example (hrpt.cif) from the previous section, you can import only measured data. In that case, the data are then automatically converted into CIF with default parameters. These can be later edited in the code.

The following measured data formats are supported:

* If standard deviations of measured intensities are present, the file should have either `*.xye` or `*.xys` extension and contain the following 3 columns:
    * [\_pd_meas.2theta\_scan](dictionaries/_pd_meas.md), 
    * [\_pd_meas.intensity\_total](dictionaries/_pd_meas.md), 
    * [\_pd_meas.intensity\_total\_su](dictionaries/_pd_meas.md).
* If standard deviations of measured intensities are not given, the file should have `*.xy` extension and contain the following 2 columns: 
    * [\_pd_meas.2theta\_scan](dictionaries/_pd_meas.md),
    * [\_pd_meas.intensity\_total](dictionaries/_pd_meas.md). 

In the second case, the standard deviations [\_pd_meas.intensity\_total\_su](dictionaries/_pd_meas.md) are calculated as the square root of the measured intensities [\_pd_meas.intensity\_total](dictionaries/_pd_meas.md).

Optional comments with `#` are possible in data file headers.

Here are some examples:

### example1.xye

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
<span class="grey"># 2theta  intensity    su</span>
   10.00     167      12.6
   10.05     157      12.5
   10.10     187      13.3
   10.15     197      14.0
   10.20     164      12.5
  ...
  164.65     173      30.1
  164.70     187      27.9
  164.75     175      38.2
  164.80     168      30.9
  164.85     109      41.2
</pre>
</div>
<!-- prettier-ignore-end -->

### example2.xy

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
<span class="grey"># 2theta  intensity</span>
   10.00     167    
   10.05     157    
   10.10     187    
   10.15     197    
   10.20     164    
  ...
  164.65     173    
  164.70     187    
  164.75     175    
  164.80     168    
  164.85     109  
</pre>
</div>
<!-- prettier-ignore-end -->

### example3.xy

<!-- prettier-ignore-start -->
<div class="cif">
<pre>
10  167.3    
10.05  157.4    
10.1  187.1    
10.15  197.8    
10.2  164.9    
...
164.65  173.3    
164.7  187.5    
164.75  175.8    
164.8  168.1    
164.85  109     
</pre>
</div>
<!-- prettier-ignore-end -->

<!-- prettier-ignore-start -->
[3]: glossary.md
<!-- prettier-ignore-end -->
