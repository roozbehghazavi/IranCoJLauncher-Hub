EmiterDef()
{
	LifeTime()
	{
		keyf(0, 1.3)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 1)
	}

	StartVelocity()
	{
		keyf(0, 450)
	}

	StartVelocityRand()
	{
		keyv(0, 0, 0, 0)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
