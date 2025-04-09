#include <iostream>
#include <omp.h>
#include <windows.h>
#include <psapi.h>
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image.h"
#include "stb_image_write.h"
#include <string>

using namespace std;

size_t getCurrentMemoryUsage()
{
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc)))
    {
        return pmc.WorkingSetSize / 1024;
    }
    return 0;
}

string getFileExtension(const string &filename)
{
    size_t dotPos = filename.find_last_of(".");
    if (dotPos == string::npos)
        return "";
    return filename.substr(dotPos + 1);
}

void sequentialGrayscale(unsigned char *img, unsigned char *grayImg, int width, int height, int channels)
{
    for (int i = 0; i < width * height; i++)
    {
        int r = img[i * channels];
        int g = img[i * channels + 1];
        int b = img[i * channels + 2];
        grayImg[i] = static_cast<unsigned char>(0.2989 * r + 0.5870 * g + 0.1140 * b);
    }
}

void parallelGrayscale(unsigned char *img, unsigned char *grayImg, int width, int height, int channels)
{
#pragma omp parallel for
    for (int i = 0; i < width * height; i++)
    {
        int r = img[i * channels];
        int g = img[i * channels + 1];
        int b = img[i * channels + 2];
        grayImg[i] = static_cast<unsigned char>(0.2989 * r + 0.5870 * g + 0.1140 * b);
    }
}

int main()
{
    size_t initialMemory = getCurrentMemoryUsage();
    cout << "Initial memory usage: " << initialMemory << " KB" << endl;

    string filename;
    cout << "Enter the image filename: ";
    cin >> filename;

    int width, height, channels;
    unsigned char *img = stbi_load(filename.c_str(), &width, &height, &channels, 0);
    if (!img)
    {
        cout << "Error: Failed to load image!" << endl;
        return -1;
    }

    cout << "Image Loaded: " << width << "x" << height << ", Channels: " << channels << endl;
    cout << "Memory after loading image: " << getCurrentMemoryUsage() << " KB" << endl;

    unsigned char *grayImgSeq = new unsigned char[width * height];
    unsigned char *grayImgPar = new unsigned char[width * height];

    // sequential
    size_t beforeSeqMem = getCurrentMemoryUsage();
    double startSeq = omp_get_wtime();
    sequentialGrayscale(img, grayImgSeq, width, height, channels);
    double endSeq = omp_get_wtime();
    size_t afterSeqMem = getCurrentMemoryUsage();

    cout << "\nSequential Processing:" << endl;
    cout << "Execution time: " << (endSeq - startSeq) << " seconds" << endl;
    cout << "Memory before: " << beforeSeqMem << " KB" << endl;
    cout << "Memory after: " << afterSeqMem << " KB" << endl;
    cout << "Memory difference: " << (afterSeqMem - beforeSeqMem) << " KB" << endl;

    // parellel
    size_t beforeParMem = getCurrentMemoryUsage();
    double startPar = omp_get_wtime();
    parallelGrayscale(img, grayImgPar, width, height, channels);
    double endPar = omp_get_wtime();
    size_t afterParMem = getCurrentMemoryUsage();

    cout << "\nParallel Processing:" << endl;
    cout << "Execution time: " << (endPar - startPar) << " seconds" << endl;
    cout << "Memory before: " << beforeParMem << " KB" << endl;
    cout << "Memory after: " << afterParMem << " KB" << endl;
    cout << "Memory difference: " << (afterParMem - beforeParMem) << " KB" << endl;

    // save
    string extension = getFileExtension(filename);
    string outputFilenameSeq = "grayscale_seq." + extension;
    string outputFilenamePar = "grayscale_par." + extension;

    if (extension == "png")
    {
        stbi_write_png(outputFilenameSeq.c_str(), width, height, 1, grayImgSeq, width);
        stbi_write_png(outputFilenamePar.c_str(), width, height, 1, grayImgPar, width);
    }
    else
    {
        stbi_write_jpg(outputFilenameSeq.c_str(), width, height, 1, grayImgSeq, 100);
        stbi_write_jpg(outputFilenamePar.c_str(), width, height, 1, grayImgPar, 100);
    }

    cout << "\nGrayscale images saved as " << outputFilenameSeq << " and " << outputFilenamePar << endl;

    stbi_image_free(img);
    delete[] grayImgSeq;
    delete[] grayImgPar;

    cout << "\nFinal memory usage: " << getCurrentMemoryUsage() << " KB" << endl;

    // o/p for py
    cout << "\n-------Data Start-------" << endl;
    cout << initialMemory << endl;
    cout << width << endl;
    cout << height << endl;
    cout << channels << endl;
    cout << beforeSeqMem << endl;
    cout << afterSeqMem << endl;
    cout << (endSeq - startSeq) << endl;
    cout << beforeParMem << endl;
    cout << afterParMem << endl;
    cout << (endPar - startPar) << endl;
    cout << getCurrentMemoryUsage() << endl;
    cout << "-------Data End-------" << endl;

    return 0;
}