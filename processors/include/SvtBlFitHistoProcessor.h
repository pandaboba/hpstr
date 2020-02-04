#ifndef __SVTBLFIT_HISTOPROCESSOR_H__
#define __SVTBLFIT_HISTOPROCESSOR_H__
#include <iostream>

//ROOT
#include "Processor.h"
#include "TFile.h"
#include "TTree.h"

//HPSTR
#include "IEvent.h"
#include "anaUtils.h"
#include "HistogramHelpers.h"
#include "BlFitHistos.h"
#include "HistoManager.h"
#include "BlFitFunction.h"

class SvtBlFitHistoProcessor : public Processor {

    public: 

        SvtBlFitHistoProcessor(const std::string& name, Process& process);
        
        ~SvtBlFitHistoProcessor();

        virtual void configure(const ParameterSet& parameters);

        virtual void initialize(std::string inFilename, std::string outFilename);

        virtual bool process();

        virtual void initialize(TTree* tree) {};

        virtual bool process(IEvent* event) {};

        virtual void finalize();

    private:

        TFile* inF_{nullptr};
	std::vector<std::string> timeSamples_{};
        //parameter defining json file
        std::string histCfgFilename_;

        //Histogram handlers
        BlFitHistos* outputHistos_{nullptr};
        HistoManager* inputHistos_{nullptr};

        //binning for profileYIterativeGauss
        int binning_{1};

        //Maps for sensor histograms and channels
        std::vector<std::string> histos2dk_{};

        //Folder where input histograms file is located
        std::string outDir_{"."};


};

#endif
