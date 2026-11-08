ParticleDef()
{
	LifeTime()
	{
		keyf(0.000000, 1.000000)
	}

	GravityMul()
	{
		keyf(0.000000, 0.020000)
	}

	Drag()
	{
		keyf(0.000000, 6.000000)
	}

	WindInfluence()
	{
		keyf(0.000000, 1.000000)
	}

	Color()
	{
		keyv4(-0.003474, 0.600418, 0.603552, 0.602365, 0.998844)
		keyv4(0.230296, 0.598331, 0.598331, 0.598331, 0.887482)
		keyv4(0.459922, 0.681511, 0.681511, 0.685472, 0.166586)
		keyv4(0.703511, 0.992193, 0.988272, 0.988272, -0.001038)
	}

	Size()
	{
		randf(0.002098, 0.917372, 22.686397)
		randf(0.950571, 9.772858, 29.172556)
		randf(1.702931, -0.092606, 40.911789)
	}

	Align("on_start")

	Material("bloodbig_particleblend.mat", "bloodbig_particleblend.mat")

	TexMultiRect(2, 2, 4)

	TexPlayMode("random_once", 1.000000)

}

