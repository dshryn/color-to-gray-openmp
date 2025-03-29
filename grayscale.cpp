#include <iostream>
#include <omp.h>
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image.h"
#include "stb_image_write.h"

using namespace std;

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
    int width, height, channels;
    unsigned char *img = stbi_load("test.jpg", &width, &height, &channels, 0);
    if (!img)
    {
        cout << "Error: Failed to load image!" << endl;
        return -1;
    }

    cout << "Image Loaded: " << width << "x" << height << ", Channels: " << channels << endl;

    unsigned char *grayImgSeq = new unsigned char[width * height];
    unsigned char *grayImgPar = new unsigned char[width * height];

    // seq
    double startSeq = omp_get_wtime();
    sequentialGrayscale(img, grayImgSeq, width, height, channels);
    double endSeq = omp_get_wtime();
    cout << "Sequential execution time: " << (endSeq - startSeq) << " seconds" << endl;

    // parellel
    double startPar = omp_get_wtime();
    parallelGrayscale(img, grayImgPar, width, height, channels);
    double endPar = omp_get_wtime();
    cout << "Parallel execution time: " << (endPar - startPar) << " seconds" << endl;

    // save
    stbi_write_jpg("grayscale_seq.jpg", width, height, 1, grayImgSeq, 100);
    stbi_write_jpg("grayscale_par.jpg", width, height, 1, grayImgPar, 100);
    cout << "Images saved as grayscale_seq.jpg and grayscale_par.jpg" << endl;

    stbi_image_free(img);
    delete[] grayImgSeq;
    delete[] grayImgPar;

    return 0;
}
