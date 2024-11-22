* src
  * easydiffraction (as before)
    * calculators (as before)
      * cryspy
        * calculator.py (instead of calculators/cryspy.py)
          * class Cryspy (as before)
        * wrapper.py (instead of Interfaces/cryspyV2.py)
          * class CryspyWrapper (instead of CryspyV2)
      * pdffit2
        * calculator.py (instead of calculators/pdffit2.py)
          * class Pdffit2 (as before)
        * wrapper.py (instead of Interfaces/pdffit2.py)
          * class Pdffit2Wrapper (instead of Pdffit2)
      * pycrysfml
        * calculator.py (instead of calculators/CFML.py)
          * class Pycrysfml (instead of CFML)
        * wrapper.py (instead of Interfaces/CFML.py)
          * class PycrysfmlWrapper (instead of CFML)
      * \_\_init\_\_.py
      * calculator_base.py (no equivalent in old API? Do we need it?)
        * class CalculatorBase (no equivalent in old API? Do we need it?)
      * wrapper_factory.py ??? (instead of interface.py)
        * class WrapperFactory ??? (instead of InterfaceFactory)
      * wrapper_base.py (instead of Interfaces/interfaceTemplate.py)
        * class WrapperBase (instead of InterfaceTemplate)




## Old structure

* easydiffraction - As before
  * calculators - As before
    * \_\_init\_\_.py - As before
    * CFML.py - Move to src/easydiffraction/calculators/pycrysfml/calculator.py
      * class CFML - Rename to Pycrysfml
    * cryspy.py - Move to src/easydiffraction/calculators/cryspy/calculator.py
      * class Cryspy - As before
    * GSASII.py - Remove
    * pdffit2.py - Move to src/easydiffraction/calculators/pdffit2/calculator.py
      * class Pdffit2 - As before
  * components - Temporarily as before
    * \_\_init\_\_.py
    * phase.py
    * polarization.py
    * site.py
  * elements - Temporarily as before
    * Backgrounds
      * \_\_init\_\_.py
      * Background.py
      * Factorial.py
      * Point.py
    * Experiments
      * \_\_init\_\_.py
      * Experiment.py
      * Pattern.py
    * \_\_init\_\_.py
  * Interfaces
    * \_\_init\_\_.py
    * CFML.py - Move to src/easydiffraction/calculators/pycrysfml/wrapper.py
      * class CFML - Rename to PycrysfmlWrapper
    * cryspy.py - Remove
    * cryspyV2.py - Move to src/easydiffraction/calculators/cryspy/wrapper.py
      * class CryspyV2 - Rename to CryspyWrapper
    * GSASII.py - Remove
    * interfaceTemplate.py - Move to src/easydiffraction/calculators/wrapper_base.py
      * class InterfaceTemplate - Rename to WrapperBase
    * pdffit2.py - Move to src/easydiffraction/calculators/pdffit2/wrapper.py
      * class Pdffit2 - Rename to Pdffit2Wrapper
    * types.py
  * io - Remove
    * \_\_init\_\_.py - Remove
    * cif.py - Remove
    * cif_reader.py - From EDB. Move to EasyCrystallography
    * cryspy_parser.py - Move to calculators/cryspy/...
    * download.py - Remove
      * def download_from_repository -> Move to easydiffraction/utils.py
    * helpers.py - Remove
  * Profiles - Temporarily as before
    * \_\_init\_\_.py
    * Analysis.py
    * common.py
    * Container.py
    * Experiment.py
    * JobType.py
    * P1D.py
    * Sample.py
  * \_\_init\_\_.py - As before
  * interfaces.py - Move to src/easydiffraction/calculators/wrapper_factory.py
    * class InterfaceFactory - Rename to WrapperFactory
  * Job.py - Rename to job.py
  * Jobs.py - Remove
  * main.py - As before
  * Runner.py - Remove
  * sample.py - Temporarily as before